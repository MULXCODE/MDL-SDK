//===- MCDwarf.h - Machine Code Dwarf support -------------------*- C++ -*-===//
//
//                     The LLVM Compiler Infrastructure
//
// This file is distributed under the University of Illinois Open Source
// License. See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//
//
// This file contains the declaration of the MCDwarfFile to support the dwarf
// .file directive and the .loc directive.
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_MC_MCDWARF_H
#define LLVM_MC_MCDWARF_H

#include "llvm/ADT/StringRef.h"
#include "llvm/Support/Compiler.h"
#include "llvm/Support/Dwarf.h"
#include "llvm/Support/raw_ostream.h"
#include <map>
#include <vector>

namespace llvm {
class MCAsmBackend;
class MCContext;
class MCSection;
class MCStreamer;
class MCSymbol;
class SourceMgr;
class SMLoc;

/// MCDwarfFile - Instances of this class represent the name of the dwarf
/// .file directive and its associated dwarf file number in the MC file,
/// and MCDwarfFile's are created and unique'd by the MCContext class where
/// the file number for each is its index into the vector of DwarfFiles (note
/// index 0 is not used and not a valid dwarf file number).
class MCDwarfFile {
  // Name - the base name of the file without its directory path.
  // The StringRef references memory allocated in the MCContext.
  StringRef Name;

  // DirIndex - the index into the list of directory names for this file name.
  unsigned DirIndex;

private: // MCContext creates and uniques these.
  friend class MCContext;
  MCDwarfFile(StringRef name, unsigned dirIndex)
      : Name(name), DirIndex(dirIndex) {}

  MCDwarfFile(const MCDwarfFile &) LLVM_DELETED_FUNCTION;
  void operator=(const MCDwarfFile &) LLVM_DELETED_FUNCTION;

public:
  /// getName - Get the base name of this MCDwarfFile.
  StringRef getName() const { return Name; }

  /// getDirIndex - Get the dirIndex of this MCDwarfFile.
  unsigned getDirIndex() const { return DirIndex; }

  /// print - Print the value to the stream \p OS.
  void print(raw_ostream &OS) const;

  /// dump - Print the value to stderr.
  void dump() const;
};

inline raw_ostream &operator<<(raw_ostream &OS, const MCDwarfFile &DwarfFile) {
  DwarfFile.print(OS);
  return OS;
}

/// MCDwarfLoc - Instances of this class represent the information from a
/// dwarf .loc directive.
class MCDwarfLoc {
  // FileNum - the file number.
  unsigned FileNum;
  // Line - the line number.
  unsigned Line;
  // Column - the column position.
  unsigned Column;
  // Flags (see #define's below)
  unsigned Flags;
  // Isa
  unsigned Isa;
  // Discriminator
  unsigned Discriminator;

// Flag that indicates the initial value of the is_stmt_start flag.
#define DWARF2_LINE_DEFAULT_IS_STMT 1

#define DWARF2_FLAG_IS_STMT (1 << 0)
#define DWARF2_FLAG_BASIC_BLOCK (1 << 1)
#define DWARF2_FLAG_PROLOGUE_END (1 << 2)
#define DWARF2_FLAG_EPILOGUE_BEGIN (1 << 3)

private: // MCContext manages these
  friend class MCContext;
  friend class MCLineEntry;
  MCDwarfLoc(unsigned fileNum, unsigned line, unsigned column, unsigned flags,
             unsigned isa, unsigned discriminator)
      : FileNum(fileNum), Line(line), Column(column), Flags(flags), Isa(isa),
        Discriminator(discriminator) {}

  // Allow the default copy constructor and assignment operator to be used
  // for an MCDwarfLoc object.

public:
  /// getFileNum - Get the FileNum of this MCDwarfLoc.
  unsigned getFileNum() const { return FileNum; }

  /// getLine - Get the Line of this MCDwarfLoc.
  unsigned getLine() const { return Line; }

  /// getColumn - Get the Column of this MCDwarfLoc.
  unsigned getColumn() const { return Column; }

  /// getFlags - Get the Flags of this MCDwarfLoc.
  unsigned getFlags() const { return Flags; }

  /// getIsa - Get the Isa of this MCDwarfLoc.
  unsigned getIsa() const { return Isa; }

  /// getDiscriminator - Get the Discriminator of this MCDwarfLoc.
  unsigned getDiscriminator() const { return Discriminator; }

  /// setFileNum - Set the FileNum of this MCDwarfLoc.
  void setFileNum(unsigned fileNum) { FileNum = fileNum; }

  /// setLine - Set the Line of this MCDwarfLoc.
  void setLine(unsigned line) { Line = line; }

  /// setColumn - Set the Column of this MCDwarfLoc.
  void setColumn(unsigned column) { Column = column; }

  /// setFlags - Set the Flags of this MCDwarfLoc.
  void setFlags(unsigned flags) { Flags = flags; }

  /// setIsa - Set the Isa of this MCDwarfLoc.
  void setIsa(unsigned isa) { Isa = isa; }

  /// setDiscriminator - Set the Discriminator of this MCDwarfLoc.
  void setDiscriminator(unsigned discriminator) {
    Discriminator = discriminator;
  }
};

/// MCLineEntry - Instances of this class represent the line information for
/// the dwarf line table entries.  Which is created after a machine
/// instruction is assembled and uses an address from a temporary label
/// created at the current address in the current section and the info from
/// the last .loc directive seen as stored in the context.
class MCLineEntry : public MCDwarfLoc {
  MCSymbol *Label;

private:
  // Allow the default copy constructor and assignment operator to be used
  // for an MCLineEntry object.

public:
  // Constructor to create an MCLineEntry given a symbol and the dwarf loc.
  MCLineEntry(MCSymbol *label, const MCDwarfLoc loc)
      : MCDwarfLoc(loc), Label(label) {}

  MCSymbol *getLabel() const { return Label; }

  // This is called when an instruction is assembled into the specified
  // section and if there is information from the last .loc directive that
  // has yet to have a line entry made for it is made.
  static void Make(MCStreamer *MCOS, const MCSection *Section);
};

/// MCLineSection - Instances of this class represent the line information
/// for a section where machine instructions have been assembled after seeing
/// .loc directives.  This is the information used to build the dwarf line
/// table for a section.
class MCLineSection {

private:
  MCLineSection(const MCLineSection &) LLVM_DELETED_FUNCTION;
  void operator=(const MCLineSection &) LLVM_DELETED_FUNCTION;

public:
  // Constructor to create an MCLineSection with an empty MCLineEntries
  // vector.
  MCLineSection() {}

  // addLineEntry - adds an entry to this MCLineSection's line entries
  void addLineEntry(const MCLineEntry &LineEntry, unsigned CUID) {
    MCLineDivisions[CUID].push_back(LineEntry);
  }

  typedef MISTD::vector<MCLineEntry> MCLineEntryCollection;
  typedef MCLineEntryCollection::iterator iterator;
  typedef MCLineEntryCollection::const_iterator const_iterator;
  typedef MISTD::map<unsigned, MCLineEntryCollection> MCLineDivisionMap;

private:
  // A collection of MCLineEntry for each Compile Unit ID.
  MCLineDivisionMap MCLineDivisions;

public:
  // Returns whether MCLineSection contains entries for a given Compile
  // Unit ID.
  bool containEntriesForID(unsigned CUID) const {
    return MCLineDivisions.count(CUID);
  }
  // Returns the collection of MCLineEntry for a given Compile Unit ID.
  const MCLineEntryCollection &getMCLineEntries(unsigned CUID) const {
    MCLineDivisionMap::const_iterator CIter = MCLineDivisions.find(CUID);
    assert(CIter != MCLineDivisions.end());
    return CIter->second;
  }
};

class MCDwarfFileTable {
public:
  //
  // This emits the Dwarf file and the line tables for all Compile Units.
  //
  static const MCSymbol *Emit(MCStreamer *MCOS);
  //
  // This emits the Dwarf file and the line tables for a given Compile Unit.
  //
  static const MCSymbol *EmitCU(MCStreamer *MCOS, unsigned ID);
};

class MCDwarfLineAddr {
public:
  /// Utility function to encode a Dwarf pair of LineDelta and AddrDeltas.
  static void Encode(MCContext &Context, int64_t LineDelta, uint64_t AddrDelta,
                     raw_ostream &OS);

  /// Utility function to emit the encoding to a streamer.
  static void Emit(MCStreamer *MCOS, int64_t LineDelta, uint64_t AddrDelta);
};

class MCGenDwarfInfo {
public:
  //
  // When generating dwarf for assembly source files this emits the Dwarf
  // sections.
  //
  static void Emit(MCStreamer *MCOS, const MCSymbol *LineSectionSymbol);
};

// When generating dwarf for assembly source files this is the info that is
// needed to be gathered for each symbol that will have a dwarf label.
class MCGenDwarfLabelEntry {
private:
  // Name of the symbol without a leading underbar, if any.
  StringRef Name;
  // The dwarf file number this symbol is in.
  unsigned FileNumber;
  // The line number this symbol is at.
  unsigned LineNumber;
  // The low_pc for the dwarf label is taken from this symbol.
  MCSymbol *Label;

public:
  MCGenDwarfLabelEntry(StringRef name, unsigned fileNumber, unsigned lineNumber,
                       MCSymbol *label)
      : Name(name), FileNumber(fileNumber), LineNumber(lineNumber),
        Label(label) {}

  StringRef getName() const { return Name; }
  unsigned getFileNumber() const { return FileNumber; }
  unsigned getLineNumber() const { return LineNumber; }
  MCSymbol *getLabel() const { return Label; }

  // This is called when label is created when we are generating dwarf for
  // assembly source files.
  static void Make(MCSymbol *Symbol, MCStreamer *MCOS, SourceMgr &SrcMgr,
                   SMLoc &Loc);
};

class MCCFIInstruction {
public:
  enum OpType {
    OpSameValue,
    OpRememberState,
    OpRestoreState,
    OpOffset,
    OpDefCfaRegister,
    OpDefCfaOffset,
    OpDefCfa,
    OpRelOffset,
    OpAdjustCfaOffset,
    OpEscape,
    OpRestore,
    OpUndefined,
    OpRegister,
    OpWindowSave
  };

private:
  OpType Operation;
  MCSymbol *Label;
  unsigned Register;
  union {
    int Offset;
    unsigned Register2;
  };
  MISTD::vector<char> Values;

  MCCFIInstruction(OpType Op, MCSymbol *L, unsigned R, int O, StringRef V)
      : Operation(Op), Label(L), Register(R), Offset(O),
        Values(V.begin(), V.end()) {
    assert(Op != OpRegister);
  }

  MCCFIInstruction(OpType Op, MCSymbol *L, unsigned R1, unsigned R2)
      : Operation(Op), Label(L), Register(R1), Register2(R2) {
    assert(Op == OpRegister);
  }

public:
  /// \brief .cfi_def_cfa defines a rule for computing CFA as: take address from
  /// Register and add Offset to it.
  static MCCFIInstruction createDefCfa(MCSymbol *L, unsigned Register,
                                       int Offset) {
    return MCCFIInstruction(OpDefCfa, L, Register, -Offset, "");
  }

  /// \brief .cfi_def_cfa_register modifies a rule for computing CFA. From now
  /// on Register will be used instead of the old one. Offset remains the same.
  static MCCFIInstruction createDefCfaRegister(MCSymbol *L, unsigned Register) {
    return MCCFIInstruction(OpDefCfaRegister, L, Register, 0, "");
  }

  /// \brief .cfi_def_cfa_offset modifies a rule for computing CFA. Register
  /// remains the same, but offset is new. Note that it is the absolute offset
  /// that will be added to a defined register to the compute CFA address.
  static MCCFIInstruction createDefCfaOffset(MCSymbol *L, int Offset) {
    return MCCFIInstruction(OpDefCfaOffset, L, 0, -Offset, "");
  }

  /// \brief .cfi_adjust_cfa_offset Same as .cfi_def_cfa_offset, but
  /// Offset is a relative value that is added/subtracted from the previous
  /// offset.
  static MCCFIInstruction createAdjustCfaOffset(MCSymbol *L, int Adjustment) {
    return MCCFIInstruction(OpAdjustCfaOffset, L, 0, Adjustment, "");
  }

  /// \brief .cfi_offset Previous value of Register is saved at offset Offset
  /// from CFA.
  static MCCFIInstruction createOffset(MCSymbol *L, unsigned Register,
                                       int Offset) {
    return MCCFIInstruction(OpOffset, L, Register, Offset, "");
  }

  /// \brief .cfi_rel_offset Previous value of Register is saved at offset
  /// Offset from the current CFA register. This is transformed to .cfi_offset
  /// using the known displacement of the CFA register from the CFA.
  static MCCFIInstruction createRelOffset(MCSymbol *L, unsigned Register,
                                          int Offset) {
    return MCCFIInstruction(OpRelOffset, L, Register, Offset, "");
  }

  /// \brief .cfi_register Previous value of Register1 is saved in
  /// register Register2.
  static MCCFIInstruction createRegister(MCSymbol *L, unsigned Register1,
                                         unsigned Register2) {
    return MCCFIInstruction(OpRegister, L, Register1, Register2);
  }

  /// \brief .cfi_window_save SPARC register window is saved.
  static MCCFIInstruction createWindowSave(MCSymbol *L) {
    return MCCFIInstruction(OpWindowSave, L, 0, 0, "");
  }

  /// \brief .cfi_restore says that the rule for Register is now the same as it
  /// was at the beginning of the function, after all initial instructions added
  /// by .cfi_startproc were executed.
  static MCCFIInstruction createRestore(MCSymbol *L, unsigned Register) {
    return MCCFIInstruction(OpRestore, L, Register, 0, "");
  }

  /// \brief .cfi_undefined From now on the previous value of Register can't be
  /// restored anymore.
  static MCCFIInstruction createUndefined(MCSymbol *L, unsigned Register) {
    return MCCFIInstruction(OpUndefined, L, Register, 0, "");
  }

  /// \brief .cfi_same_value Current value of Register is the same as in the
  /// previous frame. I.e., no restoration is needed.
  static MCCFIInstruction createSameValue(MCSymbol *L, unsigned Register) {
    return MCCFIInstruction(OpSameValue, L, Register, 0, "");
  }

  /// \brief .cfi_remember_state Save all current rules for all registers.
  static MCCFIInstruction createRememberState(MCSymbol *L) {
    return MCCFIInstruction(OpRememberState, L, 0, 0, "");
  }

  /// \brief .cfi_restore_state Restore the previously saved state.
  static MCCFIInstruction createRestoreState(MCSymbol *L) {
    return MCCFIInstruction(OpRestoreState, L, 0, 0, "");
  }

  /// \brief .cfi_escape Allows the user to add arbitrary bytes to the unwind
  /// info.
  static MCCFIInstruction createEscape(MCSymbol *L, StringRef Vals) {
    return MCCFIInstruction(OpEscape, L, 0, 0, Vals);
  }

  OpType getOperation() const { return Operation; }
  MCSymbol *getLabel() const { return Label; }

  unsigned getRegister() const {
    assert(Operation == OpDefCfa || Operation == OpOffset ||
           Operation == OpRestore || Operation == OpUndefined ||
           Operation == OpSameValue || Operation == OpDefCfaRegister ||
           Operation == OpRelOffset || Operation == OpRegister);
    return Register;
  }

  unsigned getRegister2() const {
    assert(Operation == OpRegister);
    return Register2;
  }

  int getOffset() const {
    assert(Operation == OpDefCfa || Operation == OpOffset ||
           Operation == OpRelOffset || Operation == OpDefCfaOffset ||
           Operation == OpAdjustCfaOffset);
    return Offset;
  }

  const StringRef getValues() const {
    assert(Operation == OpEscape);
    return StringRef(&Values[0], Values.size());
  }
};

struct MCDwarfFrameInfo {
  MCDwarfFrameInfo()
      : Begin(0), End(0), Personality(0), Lsda(0), Function(0), Instructions(),
        PersonalityEncoding(), LsdaEncoding(0), CompactUnwindEncoding(0),
        IsSignalFrame(false) {}
  MCSymbol *Begin;
  MCSymbol *End;
  const MCSymbol *Personality;
  const MCSymbol *Lsda;
  const MCSymbol *Function;
  MISTD::vector<MCCFIInstruction> Instructions;
  unsigned PersonalityEncoding;
  unsigned LsdaEncoding;
  uint32_t CompactUnwindEncoding;
  bool IsSignalFrame;
};

class MCDwarfFrameEmitter {
public:
  //
  // This emits the frame info section.
  //
  static void Emit(MCStreamer &streamer, MCAsmBackend *MAB,
                   bool usingCFI, bool isEH);
  static void EmitAdvanceLoc(MCStreamer &Streamer, uint64_t AddrDelta);
  static void EncodeAdvanceLoc(MCContext &Context, uint64_t AddrDelta,
                               raw_ostream &OS);
};
} // end namespace llvm

#endif

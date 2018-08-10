//===- SectionMemoryManager.h - Memory manager for MCJIT/RtDyld -*- C++ -*-===//
//
//                     The LLVM Compiler Infrastructure
//
// This file is distributed under the University of Illinois Open Source
// License. See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//
//
// This file contains the declaration of a section-based memory manager used by
// the MCJIT execution engine and RuntimeDyld.
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_EXECUTIONENGINE_SECTIONMEMORYMANAGER_H
#define LLVM_EXECUTIONENGINE_SECTIONMEMORYMANAGER_H

#include "llvm/ADT/SmallVector.h"
#include "llvm/ExecutionEngine/RuntimeDyld.h"
#include "llvm/Support/ErrorHandling.h"
#include "llvm/Support/Memory.h"

namespace llvm {

/// This is a simple memory manager which implements the methods called by
/// the RuntimeDyld class to allocate memory for section-based loading of
/// objects, usually those generated by the MCJIT execution engine.
///
/// This memory manager allocates all section memory as read-write.  The
/// RuntimeDyld will copy JITed section memory into these allocated blocks
/// and perform any necessary linking and relocations.
///
/// Any client using this memory manager MUST ensure that section-specific
/// page permissions have been applied before attempting to execute functions
/// in the JITed object.  Permissions can be applied either by calling
/// MCJIT::finalizeObject or by calling SectionMemoryManager::finalizeMemory
/// directly.  Clients of MCJIT should call MCJIT::finalizeObject.
class SectionMemoryManager : public RTDyldMemoryManager {
  SectionMemoryManager(const SectionMemoryManager&) LLVM_DELETED_FUNCTION;
  void operator=(const SectionMemoryManager&) LLVM_DELETED_FUNCTION;

public:
  SectionMemoryManager() { }
  virtual ~SectionMemoryManager();

  /// \brief Allocates a memory block of (at least) the given size suitable for
  /// executable code.
  ///
  /// The value of \p Alignment must be a power of two.  If \p Alignment is zero
  /// a default alignment of 16 will be used.
  virtual uint8_t *allocateCodeSection(uintptr_t Size, unsigned Alignment,
                                       unsigned SectionID,
                                       StringRef SectionName);

  /// \brief Allocates a memory block of (at least) the given size suitable for
  /// executable code.
  ///
  /// The value of \p Alignment must be a power of two.  If \p Alignment is zero
  /// a default alignment of 16 will be used.
  virtual uint8_t *allocateDataSection(uintptr_t Size, unsigned Alignment,
                                       unsigned SectionID,
                                       StringRef SectionName,
                                       bool isReadOnly);

  /// \brief Update section-specific memory permissions and other attributes.
  ///
  /// This method is called when object loading is complete and section page
  /// permissions can be applied.  It is up to the memory manager implementation
  /// to decide whether or not to act on this method.  The memory manager will
  /// typically allocate all sections as read-write and then apply specific
  /// permissions when this method is called.  Code sections cannot be executed
  /// until this function has been called.  In addition, any cache coherency
  /// operations needed to reliably use the memory are also performed.
  ///
  /// \returns true if an error occurred, false otherwise.
  virtual bool finalizeMemory(MISTD::string *ErrMsg = 0);

  /// \brief Invalidate instruction cache for code sections.
  ///
  /// Some platforms with separate data cache and instruction cache require
  /// explicit cache flush, otherwise JIT code manipulations (like resolved
  /// relocations) will get to the data cache but not to the instruction cache.
  ///
  /// This method is called from finalizeMemory.
  virtual void invalidateInstructionCache();

private:
  struct MemoryGroup {
      SmallVector<sys::MemoryBlock, 16> AllocatedMem;
      SmallVector<sys::MemoryBlock, 16> FreeMem;
      sys::MemoryBlock Near;
  };

  uint8_t *allocateSection(MemoryGroup &MemGroup, uintptr_t Size,
                           unsigned Alignment);

  error_code applyMemoryGroupPermissions(MemoryGroup &MemGroup,
                                         unsigned Permissions);

  MemoryGroup CodeMem;
  MemoryGroup RWDataMem;
  MemoryGroup RODataMem;
};

}

#endif // LLVM_EXECUTION_ENGINE_SECTION_MEMORY_MANAGER_H


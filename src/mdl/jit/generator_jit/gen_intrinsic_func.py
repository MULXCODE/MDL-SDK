#!/bin/env python
#*****************************************************************************
# Copyright (c) 2013-2018, NVIDIA CORPORATION. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of NVIDIA CORPORATION nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#*****************************************************************************

# This script generated signatures for compiler known functions.
#
# python 2.3 or higher is needed
#
import sys
import os
import re

def error(msg):
	"""Write a message to stderr"""
	sys.stderr.write("gen_intrinsic_func: Error: " + msg + "\n")

def warning(msg):
	"""Write a message to stderr"""
	sys.stderr.write("gen_intrinsic_func: Warning: " + msg + "\n")

def make_temp_file():
	"""Return a temporary file name"""
	fd, name = tempfile.mkstemp()
	os.close(fd)
	return name

class SignatureParser:
	"""main signature parser"""

	def __init__(self, script_name, indir, out_name, strict):
		"""constructor"""
		self.debug = False
		self.indir  = indir
		self.out_name = out_name
		self.r_intrinsic = re.compile(r"\[\[\s+intrinsic\(\)[^]]*\]\];")
		self.curr_module = ""
		self.m_intrinsics = {}
		self.m_intrinsic_mods = {}
		self.m_signatures = {}
		self.indent = 0
		self.strict = strict
		self.m_func_index = {}
		self.m_next_func_index = 0

		self.unsupported_intrinsics = {}
		self.intrinsic_modes = {}
		self.cnst_mul = {}

		# members of the generator class, a (type, name, comment) tupel
		self.m_class_members      = {}
		self.m_class_member_names = []

		#
		# ADD NEW TYPES HERE!
		#
		self.m_types = {
			"bool"       : "BB",
			"bool2"      : "B2",
			"bool3"      : "B3",
			"bool4"      : "B4",
			"int"        : "II",
			"int2"       : "I2",
			"int3"       : "I3",
			"int4"       : "I4",
			"float"      : "FF",
			"float2"     : "F2",
			"float3"     : "F3",
			"float4"     : "F4",
			"double"     : "DD",
			"double2"    : "D2",
			"double3"    : "D3",
			"double4"    : "D4",
			"color"      : "CC",
			"float2x2"   : "F22",
			"float2x3"   : "F23",
			"float2x4"   : "F24",
			"float3x2"   : "F32",
			"float3x3"   : "F33",
			"float3x4"   : "F34",
			"float4x2"   : "F42",
			"float4x3"   : "F43",
			"float4x4"   : "F44",
			"double2x2"  : "D22",
			"double2x3"  : "D23",
			"double2x4"  : "D24",
			"double3x2"  : "D32",
			"double3x3"  : "D33",
			"double3x4"  : "D34",
			"double4x2"  : "D42",
			"double4x3"  : "D43",
			"double4x4"  : "D44",

			"float[2]"   : "FA2",
			"float[3]"   : "FA3",
			"float[4]"   : "FA4",
			"float2[2]"  : "F2A2",
			"float3[2]"  : "F3A2",
			"float4[2]"  : "F4A2",
			"double[2]"  : "DA2",
			"double2[2]" : "D2A2",
			"double3[2]" : "D3A2",
			"double4[2]" : "D4A2",

			"float[<N>]" : "FAN",
			"float[N]"   : "FAn",

			"texture_2d"   : "T2",
			"texture_3d"   : "T3",
			"texture_cube" : "TC",
			"texture_ptex" : "TP",

			"string"        : "SS",
			"light_profile" : "LP",
			"size_t"        : "ZZ",

			"double *"          : "dd",
			"float *"           : "ff",
			"void  *"           : "vv",
			"Exception_state *" : "xs",
			"State_core *"      : "sc",
			"Line_buffer *"     : "lb",
			"char const *"      : "CS",

			"float[WAVELENGTH_BASE_MAX]" : "FAW",
			"coordinate_space"           : "ECS",
			"wrap_mode"                  : "EWM",
			"Res_data_pair *"            : "PT",

			# unsupported types
			"bsdf"                      : "UB",
			"edf"                       : "UE",
			"vdf"                       : "UV",
			"bsdf_measurement"          : "UM",
			"scatter_mode"              : "ESM",
			"bsdf_component[<N>]"       : "UAB",
			"edf_component[<N>]"        : "UAE",
			"vdf_component[<N>]"        : "UAV",
			"color_bsdf_component[<N>]" : "UABB",
			"color_edf_component[<N>]"  : "UAEE",
			"color[<N>]"                : "UACC",
		}

		# map type codes to suffixes for C runtime functions
		self.m_type_suffixes = {
			"BB" : "b",  # not a runtime function
			"II" : "i",  # not a runtime function
			"FF" : "f",  # used by the C-runtime
			"DD" : ""    # no suffix used by the C-runtime
		}

		# create inverse mapping
		self.m_inv_types = {}

		# C runtime functions
		self.m_c_runtime_functions = {}
		# MDL atomic runtime functions
		self.m_mdl_runtime_functions = {}

		for type, code in self.m_types.items():
			old_type = self.m_inv_types.setdefault(code, type)
			if type != old_type:
				error("type code %s is not unique, used by '%s' and '%s'" % (code, old_type, type))

	def split_signature(self, signature):
		"""Split a signature into return type and parameter types."""
		params = signature.split('_')
		ret_type = params[0]
		params = params[1:]
		if params == ['']:
			# fix for no parameters
			params = []

		return ret_type, params

	def get_atomic_type_kind(self, type_code):
		"""If type_code is an atomic value, return its value kind, else None."""
		cases = {
			"bool":          "mi::mdl::IType::TK_BOOL",
			"int":           "mi::mdl::IType::TK_INT",
			"float":         "mi::mdl::IType::TK_FLOAT",
			"double":        "mi::mdl::IType::TK_DOUBLE",
			"color":         "mi::mdl::IType::TK_COLOR",
			"string":        "mi::mdl::IType::TK_STRING",
			"light_profile": "mi::mdl::IType::TK_LIGHT_PROFILE",
		}
		return cases.get(self.m_inv_types[type_code], None)

	def get_vector_type_kind(self, type_code):
		"""If type_code is an vector value, return its type kind, else None."""
		cases = {
			"bool2":   "mi::mdl::IType::TK_BOOL",
			"bool3":   "mi::mdl::IType::TK_BOOL",
			"bool4":   "mi::mdl::IType::TK_BOOL",
			"int2":    "mi::mdl::IType::TK_INT",
			"int3":    "mi::mdl::IType::TK_INT",
			"int4":    "mi::mdl::IType::TK_INT",
			"float2":  "mi::mdl::IType::TK_FLOAT",
			"float3":  "mi::mdl::IType::TK_FLOAT",
			"float4":  "mi::mdl::IType::TK_FLOAT",
			"double2": "mi::mdl::IType::TK_DOUBLE",
			"double3": "mi::mdl::IType::TK_DOUBLE",
			"double4": "mi::mdl::IType::TK_DOUBLE",
		}
		return cases.get(self.m_inv_types[type_code], None)

	def get_vector_type_and_size(self, type_code):
		"""If type_code is an vector value, return its (element type, size) pair else None."""
		cases = {
			"bool2":   ("bool",   2),
			"bool3":   ("bool",   3),
			"bool4":   ("bool",   4),
			"int2":    ("int",    2),
			"int3":    ("int",    3),
			"int4":    ("int",    4),
			"float2":  ("float",  2),
			"float3":  ("float",  3),
			"float4":  ("float",  4),
			"double2": ("double", 2),
			"double3": ("double", 3),
			"double4": ("double", 4),
			"color":   ("float",  3)
		}
		return cases.get(self.m_inv_types[type_code], None)

	def get_matrix_type_kind(self, type_code):
		"""If type_code is an matrix value, return its type kind, else None."""
		cases = {
			"float2x2"   : "mi::mdl::IType::TK_FLOAT",
			"float2x3"   : "mi::mdl::IType::TK_FLOAT",
			"float2x4"   : "mi::mdl::IType::TK_FLOAT",
			"float3x2"   : "mi::mdl::IType::TK_FLOAT",
			"float3x3"   : "mi::mdl::IType::TK_FLOAT",
			"float3x4"   : "mi::mdl::IType::TK_FLOAT",
			"float4x2"   : "mi::mdl::IType::TK_FLOAT",
			"float4x3"   : "mi::mdl::IType::TK_FLOAT",
			"float4x4"   : "mi::mdl::IType::TK_FLOAT",
			"double2x2"  : "mi::mdl::IType::TK_DOUBLE",
			"double2x3"  : "mi::mdl::IType::TK_DOUBLE",
			"double2x4"  : "mi::mdl::IType::TK_DOUBLE",
			"double3x2"  : "mi::mdl::IType::TK_DOUBLE",
			"double3x3"  : "mi::mdl::IType::TK_DOUBLE",
			"double3x4"  : "mi::mdl::IType::TK_DOUBLE",
			"double4x2"  : "mi::mdl::IType::TK_DOUBLE",
			"double4x3"  : "mi::mdl::IType::TK_DOUBLE",
			"double4x4"  : "mi::mdl::IType::TK_DOUBLE",
		}
		return cases.get(self.m_inv_types[type_code], None)

	def get_texture_shape(self, type_code):
		"""If type_code is a texture type, return its shape, else None."""
		cases = {
			"texture_2d"   : "mi::mdl::IType_texture::TS_2D",
			"texture_3d"   : "mi::mdl::IType_texture::TS_3D",
			"texture_cube" : "mi::mdl::IType_texture::TS_CUBE",
			"texture_ptex" : "mi::mdl::IType_texture::TS_PTEX",
		}
		return cases.get(self.m_inv_types[type_code], None)

	def get_array_element_type(self, type_code):
		"""If type_code is an array type, returns its element type (code), else None."""
		cases = {
			"FA2"  : "FF",
			"FA3"  : "FF",
			"FA4"  : "FF",
			"F2A2" : "F2",
			"F3A2" : "F3",
			"F4A2" : "F4",
			"DA2"  : "DD",
			"D2A2" : "D2",
			"D3A2" : "D3",
			"D4A2" : "D4",
		}
		return cases.get(type_code, None)

	def do_indentation(self, f):
		"""Print current indentation."""
		for i in range(self.indent):
			f.write("    ")

	def write(self, f, s):
		"""write string s to file f after doing indent."""
		i = 0
		for c in s:
			if c != '\n':
				break
			f.write(c)
			i += 1
		s = s[i:]
		if s == "":
			return
		self.do_indentation(f)
		f.write(s)

	def format_code(self, f, code):
		"""The (not so) smart code formater."""
		skip_spaces = True
		for c in code:
			if skip_spaces:
				# skip spaces
				if c == '\n':
					f.write(c)
				if c.isspace():
					continue
				if c == '}' or c == ')':
					self.indent -= 1
				self.do_indentation(f)
				skip_spaces = False
				if c == '}' or c == ')':
					f.write(c)
					continue

			if not skip_spaces:
				# copy mode
				f.write(c)
				if c == '\n':
					skip_spaces = True
				elif c == '{' or c == '(':
					self.indent += 1
				elif c == '}' or c == ')':
					self.indent -= 1

	def parse(self, mdl_name):
		"""Parse a mdl module."""
		self.curr_module = mdl_name
		fname = self.indir + "/" + mdl_name + ".mdl"
		f = open(fname, "r")
		o = self.parse_file(f)
		f.close()

	def as_intrinsic_function(self, decl):
		"""Check if the given declaration is an intrinsic function declaration."""
		if decl[:5] == "const":
			return None
		if decl[:4] == "enum":
			return None
		if decl[:5] == "struct":
			return None
		if decl[:8] == "material":
			return None
		m = self.r_intrinsic.search(decl)
		if m:
			decl = decl[:m.start()]
			# kill all other annotations
			return re.sub(r'\[\[[^]]*\]\]', "", decl).strip()
		return None

	def get_type(self, tokens):
		"""decode a type"""
		start = 0
		end   = 1
		if tokens[0] == "uniform" or tokens[0] == "varying":
			# skip uniform and varying modifier
			end += 1
			start += 1
		ret_type = " ".join(tokens[start:end])

		return tokens[end:], ret_type

	def do_get_type_code(self, s):
		"""get the type code"""
		try:
			return self.m_types[s]
		except KeyError, e:
			error("Unsupported type '" + s + "' found")
			sys.exit(1)

	def get_type_suffix(self, s):
		"""get the type suffix"""
		try:
			return self.m_type_suffixes[s]
		except KeyError, e:
			error("Unsupported type '" + s + "' found")
			sys.exit(1)


	def get_type_code(self, s):
		"""get the type code"""
		c = self.do_get_type_code(s)

		return c

	def create_signature(self, ret_type, args):
		"""create the signature"""
		ret_tp = self.get_type_code(ret_type)
		sig    = "_"

		comma = ''
		for arg in args:
			sig += comma + self.get_type_code(arg)
			comma = '_'

		return ret_tp + sig

	def is_float_type(self, type_code):
		"""If type_code is an float type, return True, else False."""
		cases = {
			"float":  True,
			"double": True,
		}
		return cases.get(self.m_inv_types[type_code], False)

	def is_int_type(self, type_code):
		"""If type_code is an int type, return True, else False."""
		return self.m_inv_types[type_code] == "int"

	def is_bool_type(self, type_code):
		"""If type_code is a bool type, return True, else False."""
		return self.m_inv_types[type_code] == "bool"

	def is_atomic_type(self, type_code):
		"""If type_code is a bool, int, or float type, return True, else False."""
		return self.is_bool_type(type_code) or self.is_int_type(type_code) or self.is_float_type(type_code)

	def register_runtime_func(self, fname, signature):
		"""Register a C runtime function by name and signature."""
		if self.m_c_runtime_functions.get(fname) != None:
			error("C runtime function '%' already registzered\n", fname)
		self.m_c_runtime_functions[fname] = signature

	def register_mdl_runtime_func(self, fname, signature):
		"""Register a mdl runtime function by name and signature."""
		if self.m_mdl_runtime_functions.get(fname) != None:
			error("MDL runtime function '%' already registzered\n", fname)
		self.m_mdl_runtime_functions[fname] = signature

	def is_state_supported(self, name, signature):
		"""Checks if the given state intrinsic is supported."""
		if (name == "normal" or name == "geometry_normal" or name == "position" or
				name == "animation_time"):
			self.intrinsic_modes[name + signature] = "state::core_set"
			return True
		elif name == "rounded_corner_normal":
			self.intrinsic_modes[name + signature] = "state::rounded_corner_normal"
			return True
		elif name == "texture_coordinate":
			self.intrinsic_modes[name + signature] = "state::texture_coordinate"
			return True
		elif name == "texture_space_max":
			self.intrinsic_modes[name + signature] = "state::texture_space_max"
			return True
		elif name == "texture_tangent_u":
			self.intrinsic_modes[name + signature] = "state::texture_tangent_u"
			return True
		elif name == "texture_tangent_v":
			self.intrinsic_modes[name + signature] = "state::texture_tangent_v"
			return True
		elif name == "direction":
			self.intrinsic_modes[name + signature] = "state::environment_set"
			return True
		elif name == "transform":
			self.intrinsic_modes[name + signature] = "state::transform"
			return True
		elif name == "transform_point":
			self.intrinsic_modes[name + signature] = "state::transform_point"
			return True
		elif name == "transform_vector":
			self.intrinsic_modes[name + signature] = "state::transform_vector"
			return True
		elif name == "transform_normal":
			self.intrinsic_modes[name + signature] = "state::transform_normal"
			return True
		elif name == "transform_scale":
			self.intrinsic_modes[name + signature] = "state::transform_scale"
			return True
		elif (name == "meters_per_scene_unit" or name == "scene_units_per_meter" or
				name == "object_id" or name == "wavelength_min" or name == "wavelength_max"):
			# these should be handled by the code generator directly and never be
			# called here
			self.intrinsic_modes[name + signature] = "state::zero_return"
			return True
		else:
			#warning("state::%s() will be mapped to zero" % name)
			self.intrinsic_modes[name + signature] = "state::zero_return"
			return True
		return False

	def is_df_supported(self, name, signature):
		"""Checks if the given df intrinsic is supported."""
		ret_type, params = self.split_signature(signature)

		if (name == "diffuse_reflection_bsdf" or
			name == "diffuse_transmission_bsdf" or
			name == "specular_bsdf" or
			name == "simple_glossy_bsdf" or
			name == "backscattering_glossy_reflection_bsdf" or
			name == "measured_bsdf" or
			name == "microfacet_beckmann_smith_bsdf" or
			name == "microfacet_ggx_smith_bsdf" or
			name == "microfacet_beckmann_vcavities_bsdf" or
			name == "microfacet_ggx_vcavities_bsdf" or
			name == "ward_geisler_moroder_bsdf" or
			name == "diffuse_edf" or
			name == "spot_edf" or
			name == "measured_edf" or
			name == "anisotropic_vdf" or
			name == "tint" or
			name == "thin_film" or
			name == "directional_factor" or
			name == "normalized_mix" or
			name == "clamped_mix" or
			name == "weighted_layer" or
			name == "fresnel_layer" or
			name == "custom_curve_layer" or
			name == "measured_curve_layer" or
			name == "measured_curve_factor" or
			name == "color_normalized_mix" or
			name == "color_clamped_mix" or
			name == "color_weighted_layer" or
			name == "color_fresnel_layer" or
			name == "color_custom_curve_layer" or
			name == "color_measured_curve_layer" or
			name == "fresnel_factor"):
			self.unsupported_intrinsics[name] = "unsupported"
			return True;
		if (name == "light_profile_power" or name == "light_profile_maximum" or
				name == "light_profile_isvalid"):
			if len(params) == 1:
				# support light_profile_power(), light_profile_maximum(), light_profile_isvalid()
				self.intrinsic_modes[name + signature] = "df::attr_lookup"
				return True
		elif name == "bsdf_measurement_isvalid":
			if len(params) == 1:
				# support bsdf_measurement_isvalid()
				self.intrinsic_modes[name + signature] = "df::attr_lookup"
				return True
		return False

	def is_tex_supported(self, name, signature):
		"""Checks if the given tex intrinsic is supported."""
		ret_type, params = self.split_signature(signature)

		if name == "width" or name == "height":
			if (len(params) == 1):
				# support width(), height() without uv_tile parameter
				self.intrinsic_modes[name + signature] = "tex::attr_lookup"
				return True
			if (params[0] == "T2" and len(params) == 2):
				# support width(), height() with uv_tile parameter
				self.intrinsic_modes[name + signature] = "tex::attr_lookup_uvtile"
				return True
		elif name == "depth" or name == "texture_isvalid":
			if len(params) == 1:
				# support depth(), texture_isvalid()
				self.intrinsic_modes[name + signature] = "tex::attr_lookup"
				return True
		elif name == "lookup_float":
			# support lookup_float()
			self.intrinsic_modes[name + signature] = "tex::lookup_float"
			return True
		elif (name == "lookup_float2" or name == "lookup_float3" or
				name == "lookup_float4" or name == "lookup_color"):
			# support lookup_float2|3|4|color()
			self.intrinsic_modes[name + signature] = "tex::lookup_floatX"
			return True
		elif name == "texel_float":
			if (len(params) == 2):
				# support texel_float() without uv_tile parameter
				self.intrinsic_modes[name + signature] = "tex::texel_float"
				return True
			if (params[0] == "T2" and len(params) == 3):
				# support texel_float(texture_2d) with uv_tile parameter
				self.intrinsic_modes[name + signature] = "tex::texel_float_uvtile"
				return True
		elif (name == "texel_float2" or name == "texel_float3" or
			 name == "texel_float4" or name == "texel_color"):
			if (len(params) == 2):
				# support texel_float2|3|4|color() without uv_tile parameter
				self.intrinsic_modes[name + signature] = "tex::texel_floatX"
				return True
			if (params[0] == "T2" and len(params) == 3):
				# support texel_float2|3|4|color(texture_2d) with uv_tile parameter
				self.intrinsic_modes[name + signature] = "tex::texel_floatX_uvtile"
				return True
		return False

	def is_debug_supported(self, name, signature):
		"""Checks if the given debug intrinsic is supported."""
		ret_type, params = self.split_signature(signature)

		if name == "breakpoint":
			if len(params) == 0:
				# support breakpoint()
				self.intrinsic_modes[name + signature] = "debug::breakpoint"
				return True
		elif name == "assert":
			if len(params) == 5:
				# support assert(expr, reason)
				self.intrinsic_modes[name + signature] = "debug::assert"
				return True
		elif name == "print":
			if len(params) == 1 or len(params) == 3:
				# support print()
				self.intrinsic_modes[name + signature] = "debug::print"
				return True
		return False

	def is_math_supported(self, name, signature):
		"""Checks if the given math intrinsic is supported."""
		ret_type, params = self.split_signature(signature)

		base = None
		dim  = 0
		vt = self.get_vector_type_and_size(ret_type)
		if vt:
			base = vt[0]
			dim  = vt[1]

		all_atomic    = self.is_atomic_type(ret_type)
		all_base_same = base != None
		for param in params:
			if not self.is_atomic_type(param):
				all_atomic = False
			if self.m_inv_types[param] != base:
				vt = self.get_vector_type_and_size(param)
				if not vt or vt[0] != base or vt[1] != dim:
					all_base_same = False

		if len(params) == 3:
			if name == "lerp":
				# support lerp with 3 arguments
				self.intrinsic_modes[name + signature] = "math::lerp"
				return True
		elif len(params) == 2:
			if name == "dot":
				# support dot with 2 arguments
				self.intrinsic_modes[name + signature] = "math::dot"
				return True
			elif name == "min" or name == "max":
				# support min/max with 2 arguments
				self.intrinsic_modes[name + signature] = "math::min|max"
				return True
			elif name == "step":
				# support step with 2 arguments
				self.intrinsic_modes[name + signature] = "math::step"
				return True
			elif name == "distance":
				# support distance(floatX)
				self.intrinsic_modes[name + signature] = "math::distance"
				return True
			elif name == "emission_color":
				# unsupported emission_color(float[<N>], float[N]), emission_color(color)
				self.unsupported_intrinsics[name] = "unsupported"
				return True
		elif len(params) == 1:
			if name == "any" or name == "all":
				# support any and all with one argument
				self.intrinsic_modes[name + signature] = "math::any|all"
				return True
			if name == "average":
				# support average with one argument
				self.intrinsic_modes[name + signature] = "math::average"
				return True
			elif name == "degrees":
				# support degrees with 1 argument
				self.intrinsic_modes[name + signature] = "math::const_mul"
				self.cnst_mul[name] = "180.0 / M_PI"
				return True
			elif name == "radians":
				# support radians with 1 argument
				self.intrinsic_modes[name + signature] = "math::const_mul"
				self.cnst_mul[name] = "M_PI / 180.0"
				return True
			elif name == "min_value" or name == "max_value":
				# support min_value/max_value with 1 argument
				self.intrinsic_modes[name + signature] = "math::min_value|max_value"
				return True
			elif name == "isnan" or name == "isfinite":
				if self.get_vector_type_and_size(params[0]) or self.is_atomic_type(params[0]):
					# support all isnan/isfinite with one argument
					self.intrinsic_modes[name + signature] = "math::isnan|isfinite"
					return True
			elif name == "blackbody":
				# support blackbody with 1 argument
				self.intrinsic_modes[name + signature] = "math::blackbody"
				return True
			elif name == "length":
				# support length(floatX)
				self.intrinsic_modes[name + signature] = "math::length"
				return True
			elif name == "normalize":
				# support normalize(floatX)
				self.intrinsic_modes[name + signature] = "math::normalize"
				return True

		if all_atomic and self.is_atomic_type(ret_type):
			# simple all float/int/bool functions
			self.intrinsic_modes[name + signature] = "math::all_atomic"
			return True

		if len(params) == 1:
			if name == "luminance":
				if params[0] == "F3" or params[0] == "CC":
					# support luminance(float3) and luminance(color)
					self.intrinsic_modes[name + signature] = "math::luminance"
					return True
			elif name == "transpose":
				if self.get_matrix_type_kind(params[0]):
					# support transpose(floatX)
					self.intrinsic_modes[name + signature] = "math::transpose"
					return True

		if name == "cross":
			if signature == "F3_F3_F3" or signature == "D3_D3_D3":
				# the only supported cross variant
				self.intrinsic_modes[name + signature] = "math::cross"
				return True
			else:
				return False

		if name == "sincos":
			if len(params) == 1:
				arg_tp = params[0]
				if self.is_float_type(arg_tp):
					# support sincos for float types
					self.intrinsic_modes[name + signature] = "math::sincos"
					return True
				vt = self.get_vector_type_and_size(arg_tp)
				if vt and (vt[0] == "float" or vt[0] == "double"):
					# support sincos for float vector types
					self.intrinsic_modes[name + signature] = "math::sincos"
					return True
			return False

		if name == "modf":
			if len(params) == 1:
				arg_tp = params[0]
				if self.is_float_type(arg_tp):
					# support modf for float types
					self.intrinsic_modes[name + signature] = "math::modf"
					return True
				vt = self.get_vector_type_and_size(arg_tp)
				if vt and (vt[0] == "float" or vt[0] == "double"):
					# support modf for float vector types
					self.intrinsic_modes[name + signature] = "math::modf"
					return True
			return False

		if all_base_same:
			# assume component operation
			self.intrinsic_modes[name + signature] = "math::component_wise"
			return True

		return False

	def is_supported(self, modname, name, signature):
		"""Checks if the given intrinsic is supported."""
		if modname == "math":
			return self.is_math_supported(name, signature)
		elif modname == "state":
			return self.is_state_supported(name, signature)
		elif modname == "df":
			return self.is_df_supported(name, signature)
		elif modname == "tex":
			return self.is_tex_supported(name, signature)
		elif modname == "debug":
			return self.is_debug_supported(name, signature)
		return False

	def skip_until(self, token_set, tokens):
		"""skip tokens until token_kind is found, handle parenthesis"""
		r = 0
		e = 0
		g = 0
		a = 0
		l = len(tokens)
		while l > 0:
			tok = tokens[0]
			if r == 0 and e == 0 and g == 0 and a == 0 and tok in token_set:
				return tokens
			if tok == '(':
				r += 1
			elif tok == ')':
				r -= 1
			elif tok == '[':
				e += 1
			elif tok == ']':
				e -= 1
			elif tok == '{':
				g += 1
			elif tok == '}':
				g -= 1
			elif tok == '[[':
				a += 1
			elif tok == ']]':
				a -= 1
			tokens = tokens[1:]
			l -= 1

		# do not return empty tokens, the parser do not like that
		return [None]

	def get_signature(self, decl):
		"""Get the signature for a given function declaration."""
		# poor man's scanner :-)
		tokens = re.sub(r'[,()]', lambda m: ' ' + m.group(0) + ' ', decl).split()

		tokens, ret_type = self.get_type(tokens)

		name = tokens[0]

		self.m_intrinsic_mods[name] = self.curr_module

		if tokens[1] != '(':
			error("unknown token '" + tokens[1] + "' while processing '" + decl + "': '(' expected")
			sys.exit(1)

		tokens = tokens[2:]

		args = []

		if tokens[0] != ')':
			while True:
				tokens, t = self.get_type(tokens)
				args.append(t)

				# throw away the name
				tokens = tokens[1:]

				if tokens[0] == '=':
					# default argument
					tokens = self.skip_until({',':None, ')':None}, tokens[1:])
				if tokens[0] == ')':
					break
				if tokens[0] != ',':
					error("unknown token '" + tokens[1] + "' while processing '"
						  + decl + "': ',' expected")
					sys.exit(1)
				# skip the comma
				tokens = tokens[1:]

		signature = self.create_signature(ret_type, args)

		if self.debug:
			print decl, signature

		if self.is_supported(self.curr_module, name, signature):
			# insert the new signature for the given name
			sigs = self.m_intrinsics.setdefault(name, {})
			sigs[signature] = True

			# remember the signature (without return type)
			_, params = self.split_signature(signature)
			self.m_signatures["_".join(params)] = True
		else:
			warning("Cannot generate code for %s" % decl)

	def parse_file(self, f):
		"""Parse a file and retrieve intrinsic function definitions."""

		start = False
		curr_line = ""
		for line in f.readlines():
			l = line.strip();

			# strip line comments
			idx = l.find('//')
			if idx != -1:
				l = l[:idx]

			if not start:
				if l[:6] == "export":
					start = True
					curr_line = l[7:].strip()
			else:
				curr_line += l
			if start:
				if l[-1] == ";":
					start = False
					decl = self.as_intrinsic_function(curr_line)
					if not decl:
						continue
					if self.debug:
						print decl
					self.get_signature(decl)

	def gen_condition(self, f, params, as_assert, pre_if = ""):
		"""Generate the condition for the parameter type check."""
		if len(params) == 0:
			# we don't need a check if no parameters exists
			return False
		if as_assert:
			self.write(f, "MDL_ASSERT(check_sig_%s(f_type));\n" % "_".join(params))
			return False
		else:
			self.write(f, "%sif (check_sig_%s(f_type)) {\n" % (pre_if, "_".join(params)))
			return True

	def get_mangled_state_func_name(self, intrinsic, first_ptr_param):
		has_index = intrinsic in ["texture_coordinate", "texture_tangent_u", "texture_tangent_v",
			"tangent_space", "geometry_tangent_u", "geometry_tangent_v"]

		name = "_ZN5state%d%sE" % (len(intrinsic), intrinsic)
		if first_ptr_param:
			# one of the non-const functions?
			if intrinsic in ["set_normal", "get_texture_results"]:
				name += "P%d%s" % (len(first_ptr_param), first_ptr_param)
			else:
				name += "PK%d%s" % (len(first_ptr_param), first_ptr_param)
		if has_index:
			name += "PK15Exception_statei"  # throws due to out-of-bounds check

		if intrinsic.startswith("transform"):
			name += "NS_16coordinate_spaceES3_"
		if intrinsic in ["transform_point", "transform_vector", "transform_normal"]:
			name += "Dv3_f"
		elif intrinsic == "transform_scale":
			name += "f"

		# only version 1.3 variant
		if intrinsic == "rounded_corner_normal":
			name += "fcf"

		if intrinsic == "set_normal":
			name += "Dv3_f"

		return name

	def create_lazy_ir_construction(self, f, intrinsic, signature):
		"""Create a lazy IR construction call for a given intrinsic, signature pair."""
		ret_type, params = self.split_signature(signature)

		mode = self.intrinsic_modes.get(intrinsic + signature)
		func_index = self.get_function_index((intrinsic, signature))

		self.write(f, "if (llvm::Function *func = m_intrinsics[%d])\n" % func_index)
		self.indent += 1
		self.write(f, "return func;\n")
		self.indent -= 1
		mod_name = self.m_intrinsic_mods[intrinsic]

		if mod_name == "state":
			self.write(f, "if (m_use_user_state_module) {\n")
			self.indent += 1;

			self.write(f, "llvm::Function *func;\n")
			self.write(f, "if (m_code_gen.m_state_mode & Type_mapper::SSM_CORE)\n")
			self.indent += 1
			self.write(f, "func = m_code_gen.get_llvm_module()->getFunction(\"%s\");\n"
				% self.get_mangled_state_func_name(intrinsic, "State_core"))
			self.indent -= 1
			self.write(f, "else\n")
			self.indent += 1
			self.write(f, "func = m_code_gen.get_llvm_module()->getFunction(\"%s\");\n"
				% self.get_mangled_state_func_name(intrinsic, "State_environment"))
			self.indent -= 1

			self.write(f, "if (func != NULL) {\n")
			self.indent += 1
			self.write(f, "m_code_gen.create_context_data(func_def, func);\n")
			self.write(f, "return m_intrinsics[%d] = func;\n" % func_index)
			self.indent -= 1
			self.write(f, "}\n")

			self.indent -= 1
			self.write(f, "}\n")

		suffix = signature
		if suffix[-1] == '_':
			# no parameters
			suffix = suffix[:-1]
		self.write(f, "return m_intrinsics[%d] = create_%s_%s_%s(func_def);\n" % (func_index, mod_name, intrinsic, suffix))

	def create_ir_constructor(self, f, intrinsic, signature):
		"""Create the evaluation call for a given intrinsic, signature pair."""
		if self.unsupported_intrinsics.get(intrinsic):
			# we cannot create code for unsupported functions, these should not occur
			return

		mod_name = self.m_intrinsic_mods[intrinsic]

		suffix = signature
		if suffix[-1] == '_':
			# no parameters
			suffix = suffix[:-1]

		self.write(f, "/// Generate LLVM IR for %s::%s_%s()\n" % (mod_name, intrinsic, suffix))
		self.write(f, "llvm::Function *create_%s_%s_%s(mi::mdl::IDefinition const *func_def)\n" % (mod_name, intrinsic, suffix))
		self.write(f, "{\n")
		self.indent += 1
		self.create_ir_constructor_body(f, intrinsic, signature)
		self.indent -= 1
		self.write(f, "}\n\n")

	def get_runtime_enum(self, runtime_func):
		"""Return the name of the Runtime_function enum value for the given runtime function."""
		# first check for MDL runtime functions, those are more specific
		if self.m_mdl_runtime_functions.get("mdl_" + runtime_func):
			return "RT_MDL_" + runtime_func.upper()
		if self.m_c_runtime_functions.get(runtime_func):
			return "RT_" + runtime_func.upper()
		error("Unknown runtime function '%s'" % runtime_func)
		return None

	def create_ir_constructor_body(self, f, intrinsic, signature):
		"""Create the constructor body for a given intrinsic, signature pair."""

		mode = self.intrinsic_modes.get(intrinsic + signature)
		if mode == None:
			print "error: ", intrinsic + signature

		self.write(f, 'Function_instance inst(m_code_gen.get_allocator(), func_def);\n')
		self.write(f, 'LLVM_context_data *ctx_data = m_code_gen.get_or_create_context_data(NULL, inst, "::%s");\n' % self.m_intrinsic_mods[intrinsic])
		self.write(f, "llvm::Function    *func     = ctx_data->get_function();\n")

		self.write(f, "unsigned          flags     = ctx_data->get_function_flags();\n\n")

		self.write(f, "Function_context ctx(m_alloc, m_code_gen, inst, func, flags);\n")
		self.write(f, "llvm::Value *res;\n")

		ret_type, params = self.split_signature(signature)

		need_res_data = mode[0:5] == "tex::" or mode == "df::attr_lookup"

		if need_res_data or params != []:
			self.write(f, "llvm::Function::arg_iterator arg_it = ctx.get_first_parameter();\n")

		comma = '\n'
		if need_res_data:
			# first parameter is the texture_data pointer
			self.write(f, "llvm::Value *res_data = ctx.get_resource_data_parameter();")

		if params != []:
			idx = 0
			for param in params:
				f.write(comma)
				comma = '++);\n'
				self.write(f, "llvm::Value *%s = load_by_value(ctx, arg_it" % chr(ord('a') + idx))
				idx += 1

		if need_res_data or params != []:
			f.write(');\n\n')

		if mode == "math::all_atomic":
			self.write(f, "// atomic\n")
			self.write(f, "llvm::Value *call_args[%d] = {\n" % len(params))
			self.indent += 1
			idx = 0
			for param in params:
				self.write(f, "%s,\n" % chr(ord('a') + idx))
				idx += 1
			self.indent -= 1
			self.write(f, "};\n")
			suffix = self.get_type_suffix(params[0])
			enum_value = self.get_runtime_enum(intrinsic + suffix)
			self.write(f, "llvm::Function *callee = get_runtime_func(%s);\n" % enum_value)
			self.write(f, "res = ctx->CreateCall(callee, call_args);\n")

		elif mode == "math::any|all":
			vt = self.get_vector_type_and_size(params[0])
			need_or = intrinsic == "any"
			op_instr = "CreateAnd"
			if need_or:
				op_instr = "CreateOr"

			code_params = { "op_instr" : op_instr }
			a_is_vec = self.get_vector_type_and_size(params[0])
			if a_is_vec:
				code_params["size"] = a_is_vec[1]

				code = """
				llvm::Type *arg_tp = a->getType();
				if (arg_tp->isArrayTy()) {
					unsigned idxes[1];

					idxes[0] = 0u;
					res = ctx->CreateExtractValue(a, idxes);
					for (int i = 1; i < %(size)d; ++i) {
						idxes[0] = unsigned(i);

						llvm::Value *a_elem = ctx->CreateExtractValue(a, idxes);
						res = ctx->%(op_instr)s(res, a_elem);
					}
				} else {
						llvm::Value *idx = ctx.get_constant(0);
						res = ctx->CreateExtractElement(a, idx);
						for (int i = 1; i < %(size)d; ++i) {
							llvm::Value *idx    = ctx.get_constant(i);
							llvm::Value *a_elem = ctx->CreateExtractElement(a, idx);
							res = ctx->%(op_instr)s(res, a_elem);
						}
				}
				""" % code_params
			else:
				# any|all on atomics is a no-op
				code = """
				res = a;
				"""
			self.format_code(f, code)

		elif mode == "math::average":
			vt = self.get_vector_type_and_size(params[0])

			a_is_vec = self.get_vector_type_and_size(params[0])
			if a_is_vec:
				code_params = {
					"type" : a_is_vec[0],
					"size" : a_is_vec[1]
				}

				code = """
				llvm::Type *arg_tp = a->getType();
				if (arg_tp->isArrayTy()) {
					unsigned idxes[1];

					idxes[0] = 0u;
					res = ctx->CreateExtractValue(a, idxes);
					for (unsigned i = 1; i < %(size)d; ++i) {
						idxes[0] = i;

						llvm::Value *a_elem = ctx->CreateExtractValue(a, idxes);
						res = ctx->CreateFAdd(res, a_elem);
					}
				} else {
						llvm::Value *idx = ctx.get_constant(0);
						res = ctx->CreateExtractElement(a, idx);
						for (int i = 1; i < %(size)d; ++i) {
							llvm::Value *idx    = ctx.get_constant(i);
							llvm::Value *a_elem = ctx->CreateExtractElement(a, idx);
							res = ctx->CreateFAdd(res, a_elem);
						}
				}
				llvm::Value *c = ctx.get_constant(%(type)s(1)/%(type)s(%(size)d));
				res = ctx->CreateFMul(res, c);
				""" % code_params
			else:
				# average on atomics is a no-op
				code = """
				res = a;
				"""
			self.format_code(f, code)

		elif mode == "math::lerp":
			# lerp(a, b, c) = a * (1-c) + b * c;
			code = """
			llvm::Type *arg_tp = a->getType();
			if (arg_tp->isArrayTy()) {
				llvm::ArrayType *a_tp = llvm::cast<llvm::ArrayType>(arg_tp);
				llvm::Type      *e_tp = a_tp->getElementType();

				llvm::Value *one = ctx.get_constant(e_tp, 1);
				res              = llvm::ConstantAggregateZero::get(a_tp);

				unsigned idxes[1];
				bool c_is_arr = c->getType() == arg_tp;
				for (size_t i = 0, n = a_tp->getNumElements(); i < n; ++i) {
					idxes[0] = unsigned(i);

					llvm::Value *a_elem = ctx->CreateExtractValue(a, idxes);
					llvm::Value *b_elem = ctx->CreateExtractValue(b, idxes);
					llvm::Value *c_elem = c_is_arr ? ctx->CreateExtractValue(c, idxes) : c;

					llvm::Value *s  = ctx->CreateFSub(one, c_elem);
					llvm::Value *t1 = ctx->CreateFMul(a_elem, s);
					llvm::Value *t2 = ctx->CreateFMul(b_elem, c_elem);
					llvm::Value *e  = ctx->CreateFAdd(t1, t2);

					res = ctx->CreateInsertValue(res, e, idxes);
				}
			} else {
				if (arg_tp->isVectorTy()) {
					llvm::VectorType *v_tp = llvm::cast<llvm::VectorType>(arg_tp);

					if (c->getType() != arg_tp)
						c = ctx.create_vector_splat(v_tp, c);
				}
				llvm::Value *one = ctx.get_constant(arg_tp, 1);
				llvm::Value *s   = ctx->CreateFSub(one, c);
				llvm::Value *t1  = ctx->CreateFMul(a, s);
				llvm::Value *t2  = ctx->CreateFMul(b, c);
				res = ctx->CreateFAdd(t1, t2);
			}
			"""
			self.format_code(f, code)

		elif mode == "math::const_mul":
			# degrees(a) = a * 180.0/PI
			# radians(a) = a * PI/180.0
			code = """
			llvm::Type *arg_tp = a->getType();
			if (arg_tp->isArrayTy()) {
				llvm::ArrayType *a_tp = llvm::cast<llvm::ArrayType>(arg_tp);
				llvm::Type      *e_tp = a_tp->getElementType();

				llvm::Value *cnst = ctx.get_constant(e_tp, %s);
				res               = llvm::ConstantAggregateZero::get(a_tp);

				unsigned idxes[1];
				for (size_t i = 0, n = a_tp->getNumElements(); i < n; ++i) {
					idxes[0] = unsigned(i);

					llvm::Value *a_elem = ctx->CreateExtractValue(a, idxes);
					llvm::Value *e      = ctx->CreateFMul(a_elem, cnst);

					res = ctx->CreateInsertValue(res, e, idxes);
				}
			} else {
				llvm::Value *cnst = ctx.get_constant(arg_tp, %s);
				res = ctx->CreateFMul(a, cnst);
			}
			""" % (self.cnst_mul[intrinsic], self.cnst_mul[intrinsic])

			first_param = signature.split('_')[1]
			atomic_chk = self.get_atomic_type_kind(first_param)
			if atomic_chk:
				code = """
				llvm::Type *arg_tp = a->getType();
				llvm::Value *cnst = ctx.get_constant(arg_tp, %s);
				res = ctx->CreateFMul(a, cnst);
				""" % self.cnst_mul[intrinsic]

			self.format_code(f, code)

		elif mode == "math::dot":
			# dot product
			code = """
			llvm::Type *arg_tp = a->getType();
			if (arg_tp->isArrayTy()) {
				llvm::ArrayType *a_tp = llvm::cast<llvm::ArrayType>(arg_tp);
				llvm::Type      *e_tp = a_tp->getElementType();

				res = ctx.get_constant(e_tp, 0);

				unsigned idxes[1];
				for (size_t i = 0, n = a_tp->getNumElements(); i < n; ++i) {
					idxes[0] = unsigned(i);

					llvm::Value *a_elem = ctx->CreateExtractValue(a, idxes);
					llvm::Value *b_elem = ctx->CreateExtractValue(b, idxes);
					llvm::Value *t      = ctx->CreateFMul(a_elem, b_elem);

					res = ctx->CreateFAdd(res, t);
				}
			} else {
				llvm::VectorType *v_tp = llvm::cast<llvm::VectorType>(arg_tp);
				llvm::Type       *e_tp = v_tp->getElementType();

				llvm::Value *t = ctx->CreateFMul(a, b);
				res = ctx.get_constant(e_tp, 0);
				for (size_t i = 0, n = v_tp->getNumElements(); i < n; ++i) {
					llvm::Value *idx = ctx.get_constant(int(i));
					llvm::Value *e   = ctx->CreateExtractElement(t, idx);

					res = ctx->CreateFAdd(res, e);
				}
			}
			"""

			first_param = signature.split('_')[1]
			atomic_chk = self.get_atomic_type_kind(first_param)
			if atomic_chk:
				code = "res = ctx->CreateFMul(a, b);\n"
			self.format_code(f, code)

		elif mode == "math::min|max":
			# min/max
			cmp = "LT"
			if intrinsic == "max":
				cmp = "GT"

			ret_is_vec = self.get_vector_type_and_size(ret_type)

			is_integer = False
			ext = "?"
			if ret_is_vec:
				base_tp = ret_is_vec[0]
				is_integer = base_tp == "int"
			else:
				ret_is_atomic = self.get_atomic_type_kind(ret_type)
				is_integer = ret_is_atomic == "mi::mdl::IType::TK_INT"
				if is_integer:
					ext = "I"
				elif ret_is_atomic == "mi::mdl::IType::TK_FLOAT":
					ext = "F"
				elif ret_is_atomic == "mi::mdl::IType::TK_DOUBLE":
					ext = ""

			cmp_instr = "ctx->CreateFCmp(llvm::ICmpInst::FCMP_O%s" % cmp
			if is_integer:
				cmp_instr = "ctx->CreateICmp(llvm::ICmpInst::ICMP_S%s" % cmp

			a_is_vec = self.get_vector_type_and_size(params[0])
			get_a    = "ctx->CreateExtractValue(a, idxes);"
			splat_a  = ""
			if not a_is_vec:
				get_a   = "a;"
				if ret_is_vec:
					splat_a = "a = ctx.create_vector_splat(llvm::cast<llvm::VectorType>(ret_tp), a);"

			b_is_vec = self.get_vector_type_and_size(params[1])
			get_b    = "ctx->CreateExtractValue(b, idxes);"
			splat_b  = ""
			if not b_is_vec:
				get_b = "b;"
				if ret_is_vec:
					splat_b = "b = ctx.create_vector_splat(llvm::cast<llvm::VectorType>(ret_tp), b);"

			code_params = { 
				  "get_a"     : get_a,
				  "get_b"     : get_b,
				  "splat_a"   : splat_a,
				  "splat_b"   : splat_b,
				  "cmp_instr" : cmp_instr
			}

			if ret_is_vec:
				code_params["size"] = ret_is_vec[1]

				code = """
				llvm::Type *ret_tp = ctx_data->get_return_type();
				if (ret_tp->isArrayTy()) {
					unsigned idxes[1];

					res = llvm::ConstantAggregateZero::get(ret_tp);
					for (int i = 0; i < %(size)d; ++i) {
						idxes[0] = unsigned(i);

						llvm::Value *a_elem = %(get_a)s
						llvm::Value *b_elem = %(get_b)s
						llvm::Value *cmp    = %(cmp_instr)s, a_elem, b_elem);

						llvm::Value *tmp = ctx->CreateSelect(cmp, a_elem, b_elem);
						res = ctx->CreateInsertValue(res, tmp, idxes);
					}
				} else {
						%(splat_a)s
						%(splat_b)s
						llvm::Value *cmp = %(cmp_instr)s, a, b);
						res = ctx->CreateSelect(cmp, a, b);
				}
				""" % code_params
			else:
				# scalar operation
				if ext != "?":
					code = """
					llvm::Function *m_func = get_runtime_func(RT_MDL_%s%s);
					res = ctx->CreateCall2(m_func, a, b);
					""" % (intrinsic.upper(), ext)
				else:
					code = """
					llvm::Value *cmp = %(cmp_instr)s, a, b);
					res = ctx->CreateSelect(cmp, a, b);
					""" % code_params
			self.format_code(f, code)

		elif mode == "math::step":
			ret_is_vec = self.get_vector_type_and_size(ret_type)

			is_float = True
			if ret_is_vec:
				base_tp = ret_is_vec[0]
				is_float = base_tp == "float"
			else:
				ret_is_atomic = self.get_atomic_type_kind(ret_type)
				is_float = ret_is_atomic == "mi::mdl::IType::TK_FLOAT"

			a_is_vec = self.get_vector_type_and_size(params[0])
			get_a    = "ctx->CreateExtractValue(a, idxes);"
			if not a_is_vec:
				get_a = "a;"

			b_is_vec = self.get_vector_type_and_size(params[1])
			get_b    = "ctx->CreateExtractValue(b, idxes);"
			if not b_is_vec:
				get_b = "b;"

			code_params = {
				  "get_a"     : get_a,
				  "get_b"     : get_b,
			}

			if is_float:
				code_params["zero"] = "0.0f"
				code_params["one"]  = "1.0f"
			else:
				code_params["zero"] = "0.0"
				code_params["one"]  = "1.0"

			if ret_is_vec:
				code_params["size"] = ret_is_vec[1]

				code = """
				llvm::Type     *ret_tp = ctx_data->get_return_type();
				llvm::Constant *one    = ctx.get_constant(%(one)s);
				llvm::Constant *zero   = ctx.get_constant(%(zero)s);
				if (ret_tp->isArrayTy()) {
					unsigned idxes[1];

					res = llvm::ConstantAggregateZero::get(ret_tp);
					for (unsigned i = 0; i < %(size)d; ++i) {
						idxes[0] = i;

						llvm::Value *a_elem = %(get_a)s
						llvm::Value *b_elem = %(get_b)s
						llvm::Value *cmp    = ctx->CreateFCmp(llvm::ICmpInst::FCMP_OLT, b_elem, a_elem);

						llvm::Value *tmp = ctx->CreateSelect(cmp, zero, one);
						res = ctx->CreateInsertValue(res, tmp, idxes);
					}
				} else {
						zero = llvm::ConstantVector::getSplat(%(size)d, zero);
						one  = llvm::ConstantVector::getSplat(%(size)d, one);

						llvm::Value *cmp = ctx->CreateFCmp(llvm::ICmpInst::FCMP_OLT, b, a);
						res = ctx->CreateSelect(cmp, zero, one);
				}
				""" % code_params
			else:
				code = """
				llvm::Value *cmp     = ctx->CreateFCmp(llvm::ICmpInst::FCMP_OLT, b, a);
				llvm::Constant *one  = ctx.get_constant(%(one)s);
				llvm::Constant *zero = ctx.get_constant(%(zero)s);
				res = ctx->CreateSelect(cmp, zero, one);
				""" % code_params
			self.format_code(f, code)

		elif mode == "math::min_value|max_value":
			# min_value/max_value
			cmp = "LT"
			if intrinsic == "max_value":
				cmp = "GT"
			code_params = { "cmp" : cmp }

			a_is_vec = self.get_vector_type_and_size(params[0])
			if a_is_vec:
				code_params["size"] = a_is_vec[1]

				code = """
				llvm::Type *arg_tp = a->getType();
				if (arg_tp->isArrayTy()) {
					unsigned idxes[1];

					idxes[0] = 0u;
					res = ctx->CreateExtractValue(a, idxes);
					for (int i = 1; i < %(size)d; ++i) {
						idxes[0] = unsigned(i);

						llvm::Value *a_elem = ctx->CreateExtractValue(a, idxes);
						llvm::Value *cmp    = ctx->CreateFCmp(llvm::ICmpInst::FCMP_O%(cmp)s, res, a_elem);
						res = ctx->CreateSelect(cmp, res, a_elem);
					}
				} else {
						llvm::Value *idx = ctx.get_constant(0);
						res = ctx->CreateExtractElement(a, idx);
						for (int i = 1; i < %(size)d; ++i) {
							llvm::Value *idx    = ctx.get_constant(i);
							llvm::Value *a_elem = ctx->CreateExtractElement(a, idx);
							llvm::Value *cmp    = ctx->CreateFCmp(llvm::ICmpInst::FCMP_O%(cmp)s, res, a_elem);
							res = ctx->CreateSelect(cmp, res, a_elem);
						}
				}
				""" % code_params
			else:
				# min_value|max_value on atomics is a no-op
				code = """
				res = a;
				"""
			self.format_code(f, code)

		elif mode == "math::cross":
			# cross product
			code = """
			llvm::Type *res_tp = ctx_data->get_return_type();
			res = llvm::ConstantAggregateZero::get(res_tp);
			if (res_tp->isArrayTy()) {
				unsigned idxes[1];

				idxes[0] = 0u;
				llvm::Value *a_x = ctx->CreateExtractValue(a, idxes);
				llvm::Value *b_x = ctx->CreateExtractValue(b, idxes);

				idxes[0] = 1u;
				llvm::Value *a_y = ctx->CreateExtractValue(a, idxes);
				llvm::Value *b_y = ctx->CreateExtractValue(b, idxes);

				idxes[0] = 2u;
				llvm::Value *a_z = ctx->CreateExtractValue(a, idxes);
				llvm::Value *b_z = ctx->CreateExtractValue(b, idxes);

				llvm::Value *res_x = ctx->CreateFSub(
					ctx->CreateFMul(a_y, b_z),
					ctx->CreateFMul(a_z, b_y));

				idxes[0] = 0u;
				res = ctx->CreateInsertValue(res, res_x, idxes);

				llvm::Value *res_y = ctx->CreateFSub(
					ctx->CreateFMul(a_z, b_x),
					ctx->CreateFMul(a_x, b_z));

				idxes[0] = 1u;
				res = ctx->CreateInsertValue(res, res_y, idxes);

				llvm::Value *res_z = ctx->CreateFSub(
					ctx->CreateFMul(a_x, b_y),
					ctx->CreateFMul(a_y, b_x));

				idxes[0] = 2u;
				res = ctx->CreateInsertValue(res, res_z, idxes);
			} else {
				static int const yzx[] = { 1, 2, 0 };
				llvm::Value *shuffle_yzx = ctx.get_shuffle(yzx);

				static int zxy[] = { 2, 0, 1 };
				llvm::Value *shuffle_zxy = ctx.get_shuffle(zxy);

				llvm::Value *a_yzx = ctx->CreateShuffleVector(a, a, shuffle_yzx);
				llvm::Value *b_zxy = ctx->CreateShuffleVector(b, b, shuffle_zxy);

				llvm::Value *tmp1 = ctx->CreateFMul(a_yzx, b_zxy);

				llvm::Value *a_zxy = ctx->CreateShuffleVector(a, a, shuffle_zxy);
				llvm::Value *b_yzx = ctx->CreateShuffleVector(b, b, shuffle_yzx);

				llvm::Value *tmp2 = ctx->CreateFMul(a_zxy, b_yzx);

				res = ctx->CreateFSub(tmp1, tmp2);
			}
			"""
			self.format_code(f, code)

		elif mode == "math::isnan|isfinite":
			# NanN or finite check
			cmp = "ORD"
			if intrinsic == "isnan":
				cmp = "UNO"
			code_params = { "cmp" : cmp }

			a_is_vec = self.get_vector_type_and_size(params[0])
			if a_is_vec:
				code_params["size"] = a_is_vec[1]

				code = """
				llvm::Type *res_tp = ctx_data->get_return_type();
				res = llvm::ConstantAggregateZero::get(res_tp);
				if (res_tp->isArrayTy()) {
					unsigned idxes[1];
					for (int i = 0; i < %(size)d; ++i) {
						idxes[0] = unsigned(i);
						llvm::Value *a_elem = ctx->CreateExtractValue(a, idxes);
						llvm::Value *cmp    = ctx->CreateFCmp(llvm::ICmpInst::FCMP_%(cmp)s, a_elem, a_elem);

						// map the i1 result to the bool type representation
						cmp = ctx->CreateZExt(cmp, m_code_gen.m_type_mapper.get_bool_type());
						res = ctx->CreateInsertValue(res, cmp, idxes);
					}
				} else {
					llvm::Value *tmp = ctx->CreateFCmp(llvm::ICmpInst::FCMP_%(cmp)s, a, a);
					if (tmp->getType() != res_tp) {
						// convert bool type
						res = llvm::UndefValue::get(res_tp);
						for (int i = 1; i < %(size)d; ++i) {
							llvm::Value *idx  = ctx.get_constant(i);
							llvm::Value *elem = ctx->CreateExtractElement(tmp, idx);
							// map the i1 vector result to the bool type representation
							elem = ctx->CreateZExt(elem, m_code_gen.m_type_mapper.get_bool_type());
							res = ctx->CreateInsertElement(res, elem, idx);
						}
					} else {
						res = tmp;
					}
				}
				""" % code_params
			else:
				code = """
				res = ctx->CreateFCmp(llvm::ICmpInst::FCMP_%(cmp)s, a, a);
				// map the i1 result to the bool type representation
				res = ctx->CreateZExt(res, m_code_gen.m_type_mapper.get_bool_type());
				""" % code_params
			self.format_code(f, code)

		elif mode == "math::transpose":
			type_code = params[0]
			rows = int(type_code[-1])
			cols = int(type_code[-2])


			self.write(f, "llvm::Type *ret_tp = ctx_data->get_return_type();\n")
			self.write(f, "if (ret_tp->isArrayTy()) {\n")
			self.indent += 1
			self.write(f, "llvm::ArrayType *a_tp = llvm::cast<llvm::ArrayType>(ret_tp);\n")
			self.write(f, "llvm::Type      *e_tp = a_tp->getElementType();\n")
			self.write(f, "if (!e_tp->isVectorTy()) {\n")
			self.indent += 1

			self.write(f, "res = llvm::ConstantAggregateZero::get(ret_tp);\n")
			self.write(f, "unsigned src_idxes[1], tgt_idxes[1];\n")
			self.write(f, "llvm::Value *tmp;\n\n")

			for col in range(cols):
				for row in range(rows):
					tgt_idx = col * rows + row
					src_idx = row * cols + col
					self.write(f, "src_idxes[0] = %du; tmp = ctx->CreateExtractValue(a, src_idxes);\n" % src_idx)
					self.write(f, "tgt_idxes[0] = %du; res = ctx->CreateInsertValue(res, tmp, tgt_idxes);\n" % tgt_idx)
			self.indent -= 1

			self.write(f, "} else {\n")

			self.indent += 1
			self.write(f, "MDL_ASSERT(!\"NYI\");")
			self.write(f, "res = llvm::UndefValue::get(ret_tp); // NYI array of vectors\n")
			self.indent -= 1
			self.write(f, "}\n")

			self.indent -= 1
			self.write(f, "} else {\n")
			self.indent += 1
			code = "static const int idxes[] = {";

			for col in range(cols):
				for row in range(rows):
					src_idx = row * cols + col
					code = code + (" %d," % src_idx)
			self.write(f, code[0:-1] + " };\n")

			self.write(f, "llvm::Value *shuffle = ctx.get_shuffle(idxes);\n")
			self.write(f, "res = ctx->CreateShuffleVector(a, a, shuffle);\n")

			self.indent -= 1
			self.write(f, "}\n")

		elif mode == "math::sincos":
			# we known that the return type is an array, so get the element type here
			code = """
				unsigned    idxes[1];
				llvm::Value *res_0, *res_1;

				llvm::ArrayType *ret_tp = llvm::cast<llvm::ArrayType>(ctx_data->get_return_type());
				res = llvm::ConstantAggregateZero::get(ret_tp);
			"""
			self.format_code(f, code)

			elem_type = self.get_array_element_type(ret_type)
			vt = self.get_vector_type_and_size(elem_type)
			if vt:
				atom_code = self.do_get_type_code(vt[0])
				n_elems   = vt[1]

				code_params = {
					"sin_name" : "RT_SIN" + self.get_type_suffix(atom_code).upper(),
					"cos_name" : "RT_COS" + self.get_type_suffix(atom_code).upper()
				}

				code = """
					llvm::Function *sin_func = get_runtime_func(%(sin_name)s);
					llvm::Function *cos_func = get_runtime_func(%(cos_name)s);
				"""  % code_params

				is_float = False
				if atom_code == "FF":
					is_float = True
					code += """
						llvm::Function *sincos_func =
							m_has_sincosf ? get_runtime_func(RT_SINCOSF) : NULL;
					"""

				code += """
					llvm::Type     *elm_tp   = ret_tp->getElementType();

					res_0 = llvm::ConstantAggregateZero::get(elm_tp);
					res_1 = llvm::ConstantAggregateZero::get(elm_tp);
				""" % code_params

				code += """
					if (elm_tp->isArrayTy()) {
						llvm::Value *tmp;
				"""

				for i in range(n_elems):
					code += """
						idxes[0] = %du;
						tmp   = ctx->CreateExtractValue(a, idxes);
					""" % i

					if is_float:
						code += """
							if (m_has_sincosf) {
								llvm::Value *access0[] = {
									ctx.get_constant(int(0)),
									ctx.get_constant(int(%d))
								};
								llvm::Value *sinp = ctx->CreateInBoundsGEP(res, access0);
								llvm::Value *access1[] = {
									ctx.get_constant(int(1)),
									ctx.get_constant(int(%d))
								};
								llvm::Value *cosp = ctx->CreateInBoundsGEP(res, access1);
								ctx->CreateCall3(sincos_func, a, sinp, cosp);
							} else {
						""" % (i, i)

					code += """
						res_0 = ctx->CreateInsertValue(res_0, ctx->CreateCall(sin_func, tmp), idxes);
						res_1 = ctx->CreateInsertValue(res_1, ctx->CreateCall(cos_func, tmp), idxes);
					"""
					if is_float:
						code += """
							}
						"""

				code += """
					} else {
						llvm::Value *tmp, *idx;
				"""

				if is_float:
					code += """
							if (m_has_sincosf) {
								llvm::Value *sc_tmp = ctx->CreateAlloca(elm_tp);
								llvm::Value *s_tmp  = ctx.create_simple_gep_in_bounds(
									sc_tmp, ctx.get_constant(int(0)));
								llvm::Value *c_tmp  = ctx.create_simple_gep_in_bounds(
									sc_tmp, ctx.get_constant(int(1)));
					"""

					for i in range(n_elems):
						code += """
								idx = ctx.get_constant(%d);

								tmp   = ctx->CreateExtractElement(a, idx);
								ctx->CreateCall3(sincos_func, tmp, s_tmp, c_tmp);
								res_0 = ctx->CreateInsertElement(res_0, ctx->CreateLoad(s_tmp), idx);
								res_1 = ctx->CreateInsertElement(res_1, ctx->CreateLoad(c_tmp), idx);
						""" % i

					code += """
							} else {
					"""

				for i in range(n_elems):
					code += """
							idx = ctx.get_constant(%d);

							tmp   = ctx->CreateExtractElement(a, idx);
							res_0 = ctx->CreateInsertElement(res_0, ctx->CreateCall(sin_func, tmp), idx);
							res_1 = ctx->CreateInsertElement(res_1, ctx->CreateCall(cos_func, tmp), idx);
					""" % i

				if is_float:
					code += """
						}
					"""

				code += """
					}

					idxes[0] = 0;
					res = ctx->CreateInsertValue(res, res_0, idxes);
					idxes[0] = 1;
					res = ctx->CreateInsertValue(res, res_1, idxes);
				"""
				self.format_code(f, code)
			else:
				# scala code
				atom_code = elem_type

				code_params = {
					"sin_name" : "RT_SIN" + self.get_type_suffix(atom_code).upper(),
					"cos_name" : "RT_COS" + self.get_type_suffix(atom_code).upper()
				}
				if atom_code == "FF":
					code = """
						if (m_has_sincosf) {
							llvm::Function *sincos_func = get_runtime_func(RT_SINCOSF);
							res = ctx->CreateAlloca(ret_tp);
							llvm::Value *sinp = ctx.create_simple_gep_in_bounds(
								res, ctx.get_constant(int(0)));
							llvm::Value *cosp = ctx.create_simple_gep_in_bounds(
								res, ctx.get_constant(int(1)));
							ctx->CreateCall3(sincos_func, a, sinp, cosp);
							res = ctx->CreateLoad(res);
						} else {
							llvm::Function *sin_func = get_runtime_func(RT_SINF);
							llvm::Function *cos_func = get_runtime_func(RT_COSF);
							res_0 = ctx->CreateCall(sin_func, a);
							res_1 = ctx->CreateCall(cos_func, a);

							idxes[0] = 0;
							res = ctx->CreateInsertValue(res, res_0, idxes);
							idxes[0] = 1;
							res = ctx->CreateInsertValue(res, res_1, idxes);
						}
					""" % code_params
					self.format_code(f, code)
				else:
					# not float
					code = """
						llvm::Function *sin_func = get_runtime_func(%(sin_name)s);
						llvm::Function *cos_func = get_runtime_func(%(cos_name)s);
						res_0 = ctx->CreateCall(sin_func, a);
						res_1 = ctx->CreateCall(cos_func, a);

						idxes[0] = 0;
						res = ctx->CreateInsertValue(res, res_0, idxes);
						idxes[0] = 1;
						res = ctx->CreateInsertValue(res, res_1, idxes);
					""" % code_params
					self.format_code(f, code)

		elif mode == "math::modf":
			# we known thet the return type is an array, so get the element type here
			self.write(f, "unsigned    idxes[1];\n")
			self.write(f, "llvm::Value *res_0, *res_1;\n")

			self.write(f, "llvm::ArrayType *ret_tp = llvm::cast<llvm::ArrayType>(ctx_data->get_return_type());\n")
			self.write(f, "res = llvm::ConstantAggregateZero::get(ret_tp);\n")

			elem_type = self.get_array_element_type(ret_type)
			vt = self.get_vector_type_and_size(elem_type)
			if vt:
				atom_code = self.do_get_type_code(vt[0])
				n_elems   = vt[1]
				f_name    = "RT_MODF" + self.get_type_suffix(atom_code).upper()

				self.write(f, "llvm::Function *modf   = get_runtime_func(%s);\n" % f_name)
				self.write(f, "llvm::Type     *elm_tp = ret_tp->getElementType();\n")

				self.write(f, "res_0 = llvm::ConstantAggregateZero::get(elm_tp);\n")
				self.write(f, "res_1 = llvm::ConstantAggregateZero::get(elm_tp);\n")

				self.write(f, "if (elm_tp->isArrayTy()) {\n")
				self.indent += 1

				self.write(f, "llvm::Type  *t_type = llvm::cast<llvm::ArrayType>(elm_tp)->getElementType();\n")
				self.write(f, "llvm::Value *intptr = ctx.create_local(t_type, \"tmp\");\n")
				self.write(f, "llvm::Value *tmp;\n")

				for i in range(n_elems):
					self.write(f, "idxes[0] = %du;\n" % i)

					self.write(f, "tmp = ctx->CreateExtractValue(a, idxes);\n")
					self.write(f, "tmp = ctx->CreateCall2(modf, tmp, intptr);\n")
					self.write(f, "res_0 = ctx->CreateInsertValue(res_0, tmp, idxes);\n")
					self.write(f, "res_1 = ctx->CreateInsertValue(res_1, ctx->CreateLoad(intptr), idxes);\n")

				self.indent -= 1
				self.write(f, "} else {\n")
				self.indent += 1

				self.write(f, "llvm::Type  *t_type = llvm::cast<llvm::VectorType>(elm_tp)->getElementType();\n")
				self.write(f, "llvm::Value *intptr = ctx.create_local(t_type, \"tmp\");\n")
				self.write(f, "llvm::Value *tmp, *idx;\n")

				for i in range(n_elems):
					self.write(f, "idx = ctx.get_constant(%d);\n" % i)

					self.write(f, "tmp = ctx->CreateExtractElement(a, idx);\n")
					self.write(f, "tmp = ctx->CreateCall2(modf, tmp, intptr);\n")
					self.write(f, "res_0 = ctx->CreateInsertElement(res_0, tmp, idx);\n")
					self.write(f, "res_1 = ctx->CreateInsertElement(res_1, ctx->CreateLoad(intptr), idx);\n")

				self.indent -= 1
				self.write(f, "}\n")
			else:
				atom_code = elem_type
				f_name    = "RT_MODF" + self.get_type_suffix(atom_code).upper()

				self.write(f, "llvm::Function *modf = get_runtime_func(%s);\n" % f_name)
				self.write(f, "llvm::Type  *elm_tp = ret_tp->getElementType();\n")
				self.write(f, "llvm::Value *intptr = ctx.create_local(elm_tp, \"tmp\");\n")
				self.write(f, "res_0 = ctx->CreateCall2(modf, a, intptr);\n")
				self.write(f, "res_1 = ctx->CreateLoad(intptr);\n")

			self.write(f, "idxes[0] = 0;\n")
			self.write(f, "res = ctx->CreateInsertValue(res, res_0, idxes);\n");
			self.write(f, "idxes[0] = 1;\n")
			self.write(f, "res = ctx->CreateInsertValue(res, res_1, idxes);\n");

		elif mode == "math::luminance":
			vt = self.get_vector_type_and_size(params[0])
			if params[0] == "F3" or params[0] == "CC":
				# this is the code for F3, which is sRGB, the spec does not
				# specify a color space for color, so we share the code
				code = """
				llvm::Constant *c_r = ctx.get_constant(0.212671f);
				llvm::Constant *c_g = ctx.get_constant(0.715160f);
				llvm::Constant *c_b = ctx.get_constant(0.072169f);

				llvm::Type *arg_tp = a->getType();
				if (arg_tp->isArrayTy()) {
					unsigned idxes[1];
					idxes[0] = 0;
					llvm::Value *r = ctx->CreateExtractValue(a, idxes);
					res = ctx->CreateFMul(r, c_r);
					idxes[0] = 1;
					llvm::Value *g = ctx->CreateExtractValue(a, idxes);
					res = ctx->CreateFAdd(res, ctx->CreateFMul(g, c_g));
					idxes[0] = 2;
					llvm::Value *b = ctx->CreateExtractValue(a, idxes);
					res = ctx->CreateFAdd(res, ctx->CreateFMul(b, c_b));
				} else {
					llvm::Value *idx = ctx.get_constant(0);
					llvm::Value *r = ctx->CreateExtractElement(a, idx);
					res = ctx->CreateFMul(r, c_r);
					idx = ctx.get_constant(1);
					llvm::Value *g = ctx->CreateExtractElement(a, idx);
					res = ctx->CreateFAdd(res, ctx->CreateFMul(g, c_g));
					idx = ctx.get_constant(2);
					llvm::Value *b = ctx->CreateExtractElement(a, idx);
					res = ctx->CreateFAdd(res, ctx->CreateFMul(b, c_b));
				}
				"""
				self.format_code(f, code)

		elif mode == "math::dot":
			vt = self.get_vector_type_and_size(params[0])
			if vt:
				n_elems = vt[1]
				code_params = {
				   "n_elems" : n_elems
				}
				code = """
				llvm::Type *arg_tp = a->getType();
				if (arg_tp->isArrayTy()) {
					unsigned idxes[1] = { 0 };
					llvm::Value *a_elem = ctx->CreateExtractValue(a, idxes);
					llvm::Value *b_elem = ctx->CreateExtractValue(b, idxes);
					res = ctx->CreateFMul(a_elem, b_elem);
					for (unsigned i = 1; i < %(n_elems)d; ++i) {
						idxes[0] = i;
						a_elem = ctx->CreateExtractValue(a, idxes);
						b_elem = ctx->CreateExtractValue(b, idxes);
						res    = ctx->CreateFAdd(res, ctx->CreateFMul(a_elem, b_elem));
					}
				} else {
					llvm::Value *idx = ctx.get_constant(0);
					llvm::Value *a_elem = ctx->CreateExtractElement(a, idx);
					llvm::Value *b_elem = ctx->CreateExtractElement(b, idx);
					res = ctx->CreateFMul(a_elem, b_elem);
					for (int i = 1; i < %(n_elems)d; ++i) {
						idx = ctx.get_constant(i);
						a_elem = ctx->CreateExtractElement(a, idx);
						b_elem = ctx->CreateExtractElement(b, idx);
						res = ctx->CreateFAdd(res, ctx->CreateFMul(a_elem, b_elem));
					}
				}
				""" % code_params
			else:
				code = """
				res = res = ctx->CreateFMul(a, b);
				"""
			self.format_code(f, code)

		elif mode == "math::length":
			vt = self.get_vector_type_and_size(params[0])
			if vt:
				atom_code = self.do_get_type_code(vt[0])
				n_elems = vt[1]
				f_name = "RT_SQRT" + self.get_type_suffix(atom_code).upper()
				code_params = {
				   "sqrt_name" : f_name,
				   "n_elems"   : n_elems
				}
				code = """
				llvm::Function *sqrt_func = get_runtime_func(%(sqrt_name)s);
				llvm::Type     *arg_tp    = a->getType();
				if (arg_tp->isArrayTy()) {
					unsigned idxes[1] = { 0 };
					llvm::Value *tmp = ctx->CreateExtractValue(a, idxes);
					tmp = ctx->CreateFMul(tmp, tmp);
					for (unsigned i = 1; i < %(n_elems)d; ++i) {
						idxes[0] = i;
						llvm::Value *a_elem = ctx->CreateExtractValue(a, idxes);
						tmp = ctx->CreateFAdd(tmp, ctx->CreateFMul(a_elem, a_elem));
					}
					res = ctx->CreateCall(sqrt_func, tmp);
				} else {
					llvm::Value *idx = ctx.get_constant(0);
					llvm::Value *tmp = ctx->CreateExtractElement(a, idx);
					tmp = ctx->CreateFMul(tmp, tmp);
					for (int i = 1; i < %(n_elems)d; ++i) {
						idx = ctx.get_constant(i);
						llvm::Value *a_elem = ctx->CreateExtractElement(a, idx);
						tmp = ctx->CreateFAdd(tmp, ctx->CreateFMul(a_elem, a_elem));
					}
					res = ctx->CreateCall(sqrt_func, tmp);
				}
				""" % code_params
			else:
				code = """
				res = a;
				"""
			self.format_code(f, code)

		elif mode == "math::normalize":
			vt = self.get_vector_type_and_size(params[0])
			if vt:
				atom_code = self.do_get_type_code(vt[0])
				n_elems = vt[1]
				f_name = "RT_SQRT" + self.get_type_suffix(atom_code).upper()
				code_params = {
				   "sqrt_name" : f_name,
				   "n_elems"   : n_elems
				}
				code = """
				llvm::Function *sqrt_func = get_runtime_func(%(sqrt_name)s);
				llvm::Type     *arg_tp    = a->getType();

				res = llvm::ConstantAggregateZero::get(arg_tp);
				if (arg_tp->isArrayTy()) {
					unsigned idxes[1] = { 0 };
					llvm::Value *tmp = ctx->CreateExtractValue(a, idxes);
					tmp = ctx->CreateFMul(tmp, tmp);
					for (unsigned i = 1; i < %(n_elems)d; ++i) {
						idxes[0] = i;
						llvm::Value *a_elem = ctx->CreateExtractValue(a, idxes);
						tmp = ctx->CreateFAdd(tmp, ctx->CreateFMul(a_elem, a_elem));
					}
					llvm::Value *l = ctx->CreateCall(sqrt_func, tmp);
					for (unsigned i = 0; i < %(n_elems)d; ++i) {
						idxes[0] = i;
						llvm::Value *a_elem = ctx->CreateExtractValue(a, idxes);
						tmp = ctx->CreateFDiv(a_elem, l);
						res = ctx->CreateInsertValue(res, tmp, idxes);
					}
				} else {
					llvm::Value *idx = ctx.get_constant(0);
					llvm::Value *tmp = ctx->CreateExtractElement(a, idx);
					tmp = ctx->CreateFMul(tmp, tmp);
					for (int i = 1; i < %(n_elems)d; ++i) {
						idx = ctx.get_constant(i);
						llvm::Value *a_elem = ctx->CreateExtractElement(a, idx);
						tmp = ctx->CreateFAdd(tmp, ctx->CreateFMul(a_elem, a_elem));
					}
					llvm::Value *l = ctx->CreateCall(sqrt_func, tmp);
					l = ctx.create_vector_splat(llvm::cast<llvm::VectorType>(arg_tp), l);
					res = ctx->CreateFDiv(a, l);
				}
				""" % code_params
			else:
				code = """
				res = a;
				"""
			self.format_code(f, code)

		elif mode == "math::distance":
			vt = self.get_vector_type_and_size(params[0])
			if vt:
				atom_code = self.do_get_type_code(vt[0])
				n_elems = vt[1]
				f_name = "RT_SQRT" + self.get_type_suffix(atom_code).upper()
				code_params = {
				   "sqrt_name" : f_name,
				   "n_elems"   : n_elems
				}
				code = """
				llvm::Function *sqrt_func = get_runtime_func(%(sqrt_name)s);
				llvm::Type     *arg_tp    = a->getType();
				if (arg_tp->isArrayTy()) {
					unsigned idxes[1] = { 0 };
					llvm::Value *a_elem = ctx->CreateExtractValue(a, idxes);
					llvm::Value *b_elem = ctx->CreateExtractValue(b, idxes);
					llvm::Value *tmp    = ctx->CreateFSub(a_elem, b_elem);
					res = ctx->CreateFMul(tmp, tmp);
					for (unsigned i = 1; i < %(n_elems)d; ++i) {
						idxes[0] = i;
						a_elem = ctx->CreateExtractValue(a, idxes);
						b_elem = ctx->CreateExtractValue(b, idxes);
						tmp    = ctx->CreateFSub(a_elem, b_elem);
						res    = ctx->CreateFAdd(res, ctx->CreateFMul(tmp, tmp));
					}
					res = ctx->CreateCall(sqrt_func, res);
				} else {
					llvm::Value *idx    = ctx.get_constant(0);
					llvm::Value *a_elem = ctx->CreateExtractElement(a, idx);
					llvm::Value *b_elem = ctx->CreateExtractElement(b, idx);
					llvm::Value *tmp    = ctx->CreateFSub(a_elem, b_elem);
					res = ctx->CreateFMul(tmp, tmp);
					for (int i = 1; i < %(n_elems)d; ++i) {
						idx = ctx.get_constant(i);
						a_elem = ctx->CreateExtractElement(a, idx);
						b_elem = ctx->CreateExtractElement(b, idx);
						tmp    = ctx->CreateFSub(a_elem, b_elem);
						res    = ctx->CreateFAdd(res, ctx->CreateFMul(tmp, tmp));
					}
					res = ctx->CreateCall(sqrt_func, res);
				}
				""" % code_params
			else:
				atom_code = params[0]
				f_name = "RT_ABS" + self.get_type_suffix(atom_code).upper()
				code = """
				llvm::Function *abs_func = get_runtime_func(%s);
				res = ctx->CreateFSub(a, b);
				res = ctx->CreateCall(abs_func, res);
				""" % f_name
			self.format_code(f, code)

		elif mode == "math::component_wise":
			vt = self.get_vector_type_and_size(ret_type)
			# vector/color all same base arguments

			n_elems = 0
			if ret_type == "CC":
				n_elems = 3
			else:
				n_elems = vt[1]

			atom_code = self.do_get_type_code(vt[0])
			f_name = self.get_runtime_enum(intrinsic + self.get_type_suffix(atom_code))

			self.write(f, "llvm::Value *args[%d];\n" % len(params));
			self.write(f, "llvm::Value *tmp;\n\n")
			self.write(f, "llvm::Function *elem_func = get_runtime_func(%s);\n" % f_name)
			self.write(f, "llvm::Type *ret_tp = ctx_data->get_return_type();\n")
			self.write(f, "res = llvm::ConstantAggregateZero::get(ret_tp);\n")
			self.write(f, "if (ret_tp->isArrayTy()) {\n")
			self.indent += 1

			self.write(f, "unsigned idxes[1];\n")

			for i in range(n_elems):
				self.write(f, "idxes[0] = %du;\n" % i)

				idx = 0
				for param in params:
					p_name = chr(ord('a') + idx)
					if self.is_atomic_type(param):
						self.write(f, "args[%d] = %s;\n" % (idx, p_name))
					else:
						self.write(f, "args[%d] = ctx->CreateExtractValue(%s, idxes);\n" % (idx, p_name))
					idx += 1

				self.write(f, "tmp = ctx->CreateCall(elem_func, args);\n")
				self.write(f, "res = ctx->CreateInsertValue(res, tmp, idxes);\n")

			self.indent -= 1
			self.write(f, "} else {\n")
			self.indent += 1

			self.write(f, "llvm::Value *idx;\n")

			for i in range(n_elems):
				self.write(f, "idx = ctx.get_constant(%d);\n" % i)

				idx = 0
				for param in params:
					p_name = chr(ord('a') + idx)
					if self.is_atomic_type(param):
						self.write(f, "args[%d] = %s;\n" % (idx, p_name))
					else:
						self.write(f, "args[%d] = ctx->CreateExtractElement(%s, idx);\n" % (idx, p_name))
					idx += 1

				self.write(f, "tmp = ctx->CreateCall(elem_func, args);\n")
				self.write(f, "res = ctx->CreateInsertElement(res, tmp, idx);\n")

			self.indent -= 1
			self.write(f, "}\n")

		elif mode == "math::blackbody":
			code = """
			if (m_has_res_handler) {
				llvm::Function  *bb_func = get_runtime_func(RT_MDL_BLACKBODY);
				llvm::ArrayType *arr_tp  = m_code_gen.m_type_mapper.get_arr_float_3_type();
				llvm::Value     *tmp     = ctx.create_local(arr_tp, "tmp");
				ctx->CreateCall2(bb_func, tmp, a);

				llvm::Type *ret_tp = ctx_data->get_return_type();
				if (ret_tp->isArrayTy()) {
					res = ctx->CreateLoad(tmp);
				} else {
					llvm::Value *arr = ctx->CreateLoad(tmp);
					res = llvm::ConstantAggregateZero::get(ret_tp);
					for (unsigned i = 0; i < 3; ++i) {
						unsigned idxes[1] = { i };
						tmp = ctx->CreateExtractValue(arr, idxes);
						llvm::Value *idx = ctx.get_constant(int(i));
						res = ctx->CreateInsertElement(res, tmp, idx);
					}
				}
			} else {
				res = llvm::Constant::getNullValue(ctx_data->get_return_type());
			}
			"""
			self.format_code(f, code)

		elif mode == "state::core_set":
			code = """
			llvm::Type *ret_tp = ctx_data->get_return_type();
			if (m_code_gen.m_state_mode & Type_mapper::SSM_CORE) {
				llvm::Value *state = ctx.get_state_parameter();
				llvm::Value *adr   = ctx.create_simple_gep_in_bounds(
					state, ctx.get_constant(m_code_gen.m_type_mapper.get_state_index(Type_mapper::STATE_CORE_%s)));
				res = ctx.load_and_convert(ret_tp, adr);
			} else {
				// zero in all other contexts
				res = llvm::Constant::getNullValue(ret_tp);
			}
			"""
			self.format_code(f, code % intrinsic.upper())

		elif mode == "state::rounded_corner_normal":
			code = """
			// map to state::normal"""
			idx = 0
			for param in params:
				code += """
					(void)%s;""" % chr(ord('a') + idx)
				idx = idx + 1
			code += """
			llvm::Type *ret_tp = ctx_data->get_return_type();
			if (m_code_gen.m_state_mode & Type_mapper::SSM_CORE) {
				llvm::Value *state = ctx.get_state_parameter();
				llvm::Value *adr   = ctx.create_simple_gep_in_bounds(
					state, ctx.get_constant(m_code_gen.m_type_mapper.get_state_index(Type_mapper::STATE_CORE_NORMAL)));
				res = ctx.load_and_convert(ret_tp, adr);
			} else {
				// zero in all other contexts
				res = llvm::Constant::getNullValue(ret_tp);
			}
			"""
			self.format_code(f, code)

		elif mode == "state::texture_coordinate":
			code = """
			llvm::Type *ret_tp = ctx_data->get_return_type();
			if (m_code_gen.m_state_mode & Type_mapper::SSM_CORE) {
				llvm::Value *state = ctx.get_state_parameter();
				llvm::Value *adr   = ctx.create_simple_gep_in_bounds(
					state, ctx.get_constant(m_code_gen.m_type_mapper.get_state_index(Type_mapper::STATE_CORE_%s)));
				llvm::Value *tc    = ctx->CreateLoad(adr);
				adr = ctx->CreateInBoundsGEP(tc, a);
				res = ctx.load_and_convert(ret_tp, adr);
			} else {
				// zero in all other contexts
				res = llvm::Constant::getNullValue(ret_tp);
			}
			"""
			self.format_code(f, code % intrinsic.upper())

		elif mode == "state::texture_space_max":
			code = """
			// always a runtime-constant
			res = ctx.get_constant(int(m_code_gen.m_num_texture_spaces));
			"""
			self.format_code(f, code)

		elif mode == "state::texture_tangent_v":
			code = """
			llvm::Type *ret_tp = ctx_data->get_return_type();
			if (m_code_gen.m_state_mode & Type_mapper::SSM_CORE) {
				if (m_code_gen.m_type_mapper.is_bitangents_used()) {
					// encoded as bitangent
					llvm::Value *state = ctx.get_state_parameter();
					llvm::Value *adr   = ctx.create_simple_gep_in_bounds(
						state, ctx.get_constant(m_code_gen.m_type_mapper.get_state_index(Type_mapper::STATE_CORE_BITANGENTS)));
					llvm::Value *tc    = ctx->CreateLoad(adr);
					adr = ctx->CreateInBoundsGEP(tc, a);
					// we need only xyz from the float4, so just cast it
					adr = ctx->CreateBitCast(adr, m_code_gen.m_type_mapper.get_arr_float_3_ptr_type());
					res = ctx.load_and_convert(ret_tp, adr);

					mi::mdl::IDefinition const *nz_def = m_code_gen.find_stdlib_signature("::math", "normalize(float3)");
					llvm::Function *nz_fkt = get_intrinsic_function(nz_def);
					llvm::Value *nz_args[] = { res };
					res = call_rt_func(ctx, nz_fkt, nz_args);
				} else {
					// directly encoded
					llvm::Value *state = ctx.get_state_parameter();
					llvm::Value *adr   = ctx.create_simple_gep_in_bounds(
						state, ctx.get_constant(m_code_gen.m_type_mapper.get_state_index(Type_mapper::STATE_CORE_TANGENT_V)));
					llvm::Value *tc    = ctx->CreateLoad(adr);
					adr = ctx->CreateInBoundsGEP(tc, a);
					res = ctx.load_and_convert(ret_tp, adr);
				}
			} else {
				// zero in all other contexts
				(void)a;
				res = llvm::Constant::getNullValue(ret_tp);
			}
			"""
			self.format_code(f, code)

		elif mode == "state::texture_tangent_u":
			code = """
			llvm::Type *ret_tp = ctx_data->get_return_type();
			if (m_code_gen.m_state_mode & Type_mapper::SSM_CORE) {
				if (m_code_gen.m_type_mapper.is_bitangents_used()) {
					// encoded as bitangent
					// float3 bitangent = cross(normal, tangent) * tangent_bitangentsign.w
					llvm::Value *state = ctx.get_state_parameter();
					llvm::Value *exc   = ctx.get_exc_state_parameter();

					mi::mdl::IDefinition const *n_def = m_code_gen.find_stdlib_signature("::state", "normal()");
					llvm::Function *n_fkt = get_intrinsic_function(n_def);
					llvm::Value *n_args[] = { state };
					llvm::Value *normal = call_rt_func(ctx, n_fkt, n_args);

					mi::mdl::IDefinition const *t_def = m_code_gen.find_stdlib_signature("::state", "texture_tangent_v(int)");
					llvm::Function *t_fkt = get_intrinsic_function(t_def);
					llvm::Value *t_args[] = { state, exc, a };
					llvm::Value *tangent = call_rt_func(ctx, t_fkt, t_args);

					mi::mdl::IDefinition const *c_def = m_code_gen.find_stdlib_signature("::math", "cross(float3,float3)");
					llvm::Function *c_fkt = get_intrinsic_function(c_def);
					llvm::Value *c_args[] = { normal, tangent };
					llvm::Value *cross = call_rt_func(ctx, c_fkt, c_args);

					mi::mdl::IDefinition const *nz_def = m_code_gen.find_stdlib_signature("::math", "normalize(float3)");
					llvm::Function *nz_fkt = get_intrinsic_function(nz_def);
					llvm::Value *nz_args[] = { cross };
					llvm::Value *n_cross = call_rt_func(ctx, nz_fkt, nz_args);

					llvm::Value *adr   = ctx.create_simple_gep_in_bounds(
						state, ctx.get_constant(m_code_gen.m_type_mapper.get_state_index(Type_mapper::STATE_CORE_BITANGENTS)));
					llvm::Value *tc    = ctx->CreateLoad(adr);
					adr = ctx->CreateInBoundsGEP(tc, a);
					// we need only w from the float4
					adr = ctx.create_simple_gep_in_bounds(adr, ctx.get_constant(3));
					llvm::Value *sign = ctx->CreateLoad(adr);

					res = ctx.create_mul(ret_tp, n_cross, sign);
				} else {
					// directly encoded
					llvm::Value *state = ctx.get_state_parameter();
					llvm::Value *adr   = ctx.create_simple_gep_in_bounds(
						state, ctx.get_constant(m_code_gen.m_type_mapper.get_state_index(Type_mapper::STATE_CORE_TANGENT_U)));
					llvm::Value *tc    = ctx->CreateLoad(adr);
					adr = ctx->CreateInBoundsGEP(tc, a);
					res = ctx.load_and_convert(ret_tp, adr);
				}
			} else {
				// zero in all other contexts
				(void)a;
				res = llvm::Constant::getNullValue(ret_tp);
			}
			"""
			self.format_code(f, code)

		elif mode == "state::environment_set":
			code = """
			llvm::Type *ret_tp = ctx_data->get_return_type();
			if (m_code_gen.m_state_mode & Type_mapper::SSM_ENVIRONMENT) {
				// direction exists only in environmnt context
				llvm::Value *state = ctx.get_state_parameter();
				llvm::Value *adr   = ctx.create_simple_gep_in_bounds(
					state, ctx.get_constant(Type_mapper::STATE_ENV_%s));
				res = ctx.load_and_convert(ret_tp, adr);
			} else {
				// zero in all other contexts
				res = llvm::Constant::getNullValue(ret_tp);
			}
			"""
			self.format_code(f, code % intrinsic.upper())

		elif mode == "state::transform":
			code = """
			llvm::Type  *ret_tp = ctx_data->get_return_type();
			llvm::Value *from   = a;
			llvm::Value *to     = b;

			llvm::Value *internal = ctx.get_constant(LLVM_code_generator::coordinate_internal);
			llvm::Value *encoding = ctx.get_constant(m_internal_space);

			// map internal space
			llvm::Value *f_cond = ctx->CreateICmpEQ(from, internal);
			from = ctx->CreateSelect(f_cond, encoding, from);
			llvm::Value *t_cond = ctx->CreateICmpEQ(to, internal);
			to = ctx->CreateSelect(t_cond, encoding, to);

			res = llvm::Constant::getNullValue(ret_tp);

			llvm::Value *result = ctx.create_local(ret_tp, "result");
			ctx->CreateStore(res, result);

			if (m_code_gen.m_state_mode & Type_mapper::SSM_CORE) {
				llvm::Value *cond           = ctx->CreateICmpEQ(from, to);
				llvm::BasicBlock *id_bb     = ctx.create_bb("id");
				llvm::BasicBlock *non_id_bb = ctx.create_bb("non_id");
				llvm::BasicBlock *end_bb    = ctx.create_bb("end");

				if (ret_tp->isVectorTy()) {
					// BIG vector mode

					ctx->CreateCondBr(cond, id_bb, non_id_bb);
					{
						llvm::Value *idx;

						// return the identity matrix
						ctx->SetInsertPoint(id_bb);

						llvm::Value *one = ctx.get_constant(1.0f);
						idx  = ctx.get_constant(0 * 4 + 0);
						ctx->CreateInsertElement(res, one, idx);
						idx  = ctx.get_constant(1 * 4 + 1);
						ctx->CreateInsertElement(res, one, idx);
						idx  = ctx.get_constant(2 * 4 + 2);
						ctx->CreateInsertElement(res, one, idx);
						idx  = ctx.get_constant(3 * 4 + 3);
						ctx->CreateInsertElement(res, one, idx);

						ctx->CreateStore(res, result);
						ctx->CreateBr(end_bb);
					}
					{
						ctx->SetInsertPoint(non_id_bb);

						llvm::Value *worldToObject = ctx.get_constant(LLVM_code_generator::coordinate_world);
						llvm::Value *cond = ctx->CreateICmpEQ(from, worldToObject);

						llvm::BasicBlock *w2o_bb = ctx.create_bb("w2o");
						llvm::BasicBlock *o2w_bb = ctx.create_bb("o2w");

						ctx->CreateCondBr(cond, w2o_bb, o2w_bb);
						{
							// convert w2o matrix from row major to column major
							ctx->SetInsertPoint(w2o_bb);

							llvm::Value *m_ptr = ctx.get_w2o_transform_value();

							res = llvm::Constant::getNullValue(ret_tp);
							for (int i = 0; i < 3; ++i) {
								llvm::Value *idx = ctx.get_constant(i);
								llvm::Value *ptr = ctx->CreateInBoundsGEP(m_ptr, idx);
								llvm::Value *row = ctx->CreateLoad(ptr);
								for (int j = 0; j < 4; ++j) {
									unsigned idxes[] = { unsigned(j) };
									llvm::Value *elem = ctx->CreateExtractValue(row, idxes);
									llvm::Value *idx  = ctx.get_constant(i + j * 4);
									res = ctx->CreateInsertElement(res, elem, idx);
								}
							}
							{
								// last row is always (0, 0, 0, 1)
								for (int j = 0; j < 4; ++j) {
									llvm::Value *elem = ctx.get_constant(j == 3 ? 1.0f : 0.0f);
									llvm::Value *idx  = ctx.get_constant(3 + j * 4);
									res = ctx->CreateInsertElement(res, elem, idx);
								}
							}
							ctx->CreateStore(res, result);
							ctx->CreateBr(end_bb);
						}
						{
							// convert o2w matrix from row major to column major
							ctx->SetInsertPoint(o2w_bb);

							llvm::Value *m_ptr = ctx.get_o2w_transform_value();

							res = llvm::Constant::getNullValue(ret_tp);
							for (int i = 0; i < 3; ++i) {
								llvm::Value *idx = ctx.get_constant(i);
								llvm::Value *ptr = ctx->CreateInBoundsGEP(m_ptr, idx);
								llvm::Value *row = ctx->CreateLoad(ptr);
								for (int j = 0; j < 4; ++j) {
									unsigned idxes[] = { unsigned(j) };
									llvm::Value *elem = ctx->CreateExtractValue(row, idxes);
									llvm::Value *idx  = ctx.get_constant(i + j * 4);
									res = ctx->CreateInsertElement(res, elem, idx);
								}
							}
							{
								// last row is always (0, 0, 0, 1)
								for (int j = 0; j < 4; ++j) {
									llvm::Value *elem = ctx.get_constant(j == 3 ? 1.0f : 0.0f);
									llvm::Value *idx  = ctx.get_constant(3 + j * 4);
									res = ctx->CreateInsertElement(res, elem, idx);
								}
							}
							ctx->CreateStore(res, result);
							ctx->CreateBr(end_bb);
						}
					}
					ctx->SetInsertPoint(end_bb);
				} else if (ret_tp->isArrayTy()) {
					llvm::ArrayType *arr_tp = llvm::cast<llvm::ArrayType>(ret_tp);
					llvm::Type      *e_tp   = arr_tp->getElementType();
					if (e_tp->isVectorTy()) {
						// small vector mode
						MDL_ASSERT(!"NYI");
					} else {
						// scalar mode

						ctx->CreateCondBr(cond, id_bb, non_id_bb);
						{
							// return the identity matrix
							ctx->SetInsertPoint(id_bb);

							unsigned idxes[] = { 0 * 4 + 0 };
							llvm::Value *one = ctx.get_constant(1.0f);
							ctx->CreateInsertValue(res, one, idxes);
							idxes[0] = 1 * 4 + 1;
							ctx->CreateInsertValue(res, one, idxes);
							idxes[0] = 2 * 4 + 2;
							ctx->CreateInsertValue(res, one, idxes);
							idxes[0] = 3 * 4 + 3;
							ctx->CreateInsertValue(res, one, idxes);

							ctx->CreateStore(res, result);
							ctx->CreateBr(end_bb);
						}
						{
							ctx->SetInsertPoint(non_id_bb);

							llvm::Value *worldToObject = ctx.get_constant(LLVM_code_generator::coordinate_world);
							llvm::Value *cond = ctx->CreateICmpEQ(from, worldToObject);

							llvm::BasicBlock *w2o_bb = ctx.create_bb("w2o");
							llvm::BasicBlock *o2w_bb = ctx.create_bb("o2w");

							ctx->CreateCondBr(cond, w2o_bb, o2w_bb);
							{
								// convert w2o matrix from row major to column major
								ctx->SetInsertPoint(w2o_bb);

								llvm::Value *m_ptr = ctx.get_w2o_transform_value();

								res = llvm::Constant::getNullValue(ret_tp);
								for (int i = 0; i < 3; ++i) {
									llvm::Value *idx = ctx.get_constant(i);
									llvm::Value *ptr = ctx->CreateInBoundsGEP(m_ptr, idx);
									llvm::Value *row = ctx->CreateLoad(ptr);
									for (unsigned j = 0; j < 4; ++j) {
										unsigned idxes[] = { j };
										llvm::Value *elem = ctx->CreateExtractValue(row, idxes);
										idxes[0] = unsigned(i) + j * 4;
										res = ctx->CreateInsertValue(res, elem, idxes);
									}
								}
								{
									// last row is always (0, 0, 0, 1)
									for (unsigned j = 0; j < 4; ++j) {
										unsigned idxes[] = { 3 + j * 4 };
										llvm::Value *elem = ctx.get_constant(j == 3 ? 1.0f : 0.0f);
										res = ctx->CreateInsertValue(res, elem, idxes);
									}
								}
								ctx->CreateStore(res, result);
								ctx->CreateBr(end_bb);
							}
							{
								// convert o2w matrix from row major to column major
								ctx->SetInsertPoint(o2w_bb);

								llvm::Value *m_ptr = ctx.get_o2w_transform_value();

								res = llvm::Constant::getNullValue(ret_tp);
								for (int i = 0; i < 3; ++i) {
									llvm::Value *idx = ctx.get_constant(i);
									llvm::Value *ptr = ctx->CreateInBoundsGEP(m_ptr, idx);
									llvm::Value *row = ctx->CreateLoad(ptr);
									for (unsigned j = 0; j < 4; ++j) {
										unsigned idxes[] = { j };
										llvm::Value *elem = ctx->CreateExtractValue(row, idxes);
										idxes[0] = unsigned(i) + j * 4;
										res = ctx->CreateInsertValue(res, elem, idxes);
									}
								}
								{
									// last row is always (0, 0, 0, 1)
									for (unsigned j = 0; j < 4; ++j) {
										unsigned idxes[] = { 3 + j * 4 };
										llvm::Value *elem = ctx.get_constant(j == 3 ? 1.0f : 0.0f);
										res = ctx->CreateInsertValue(res, elem, idxes);
									}
								}
								ctx->CreateStore(res, result);
								ctx->CreateBr(end_bb);
							}
						}
						ctx->SetInsertPoint(end_bb);
					}
				}
			} else {
				// zero in all other contexts
			}
			res = ctx->CreateLoad(result);
			"""
			self.format_code(f, code)

		elif mode == "state::transform_point":
			code = """
			llvm::Type  *ret_tp = ctx_data->get_return_type();
			llvm::Value *from   = a;
			llvm::Value *to     = b;
			llvm::Value *point  = c;

			llvm::Value *internal = ctx.get_constant(LLVM_code_generator::coordinate_internal);
			llvm::Value *encoding = ctx.get_constant(m_internal_space);

			// map internal space
			llvm::Value *f_cond = ctx->CreateICmpEQ(from, internal);
			from = ctx->CreateSelect(f_cond, encoding, from);
			llvm::Value *t_cond = ctx->CreateICmpEQ(to, internal);
			to = ctx->CreateSelect(t_cond, encoding, to);

			res = llvm::Constant::getNullValue(ret_tp);

			llvm::Value *result = ctx.create_local(ret_tp, "result");
			ctx->CreateStore(res, result);

			llvm::Value *cond           = ctx->CreateICmpEQ(from, to);
			llvm::BasicBlock *id_bb     = ctx.create_bb("id");
			llvm::BasicBlock *non_id_bb = ctx.create_bb("non_id");
			llvm::BasicBlock *end_bb    = ctx.create_bb("end");

			ctx->CreateCondBr(cond, id_bb, non_id_bb);
			{
				// the matrix is the identity, return the point
				ctx->SetInsertPoint(id_bb);

				ctx->CreateStore(point, result);
				ctx->CreateBr(end_bb);
			}
			{
				ctx->SetInsertPoint(non_id_bb);

				if (m_code_gen.m_state_mode & Type_mapper::SSM_CORE) {
					llvm::Value *worldToObject = ctx.get_constant(LLVM_code_generator::coordinate_world);
					llvm::Value *cond = ctx->CreateICmpEQ(from, worldToObject);

					llvm::BasicBlock *w2o_bb = ctx.create_bb("w2o");
					llvm::BasicBlock *o2w_bb = ctx.create_bb("o2w");

					if (ret_tp->isVectorTy()) {
						// vector mode
						llvm::VectorType *vec_tp = llvm::cast<llvm::VectorType>(ret_tp);

						ctx->CreateCondBr(cond, w2o_bb, o2w_bb);
						{
							ctx->SetInsertPoint(w2o_bb);

							llvm::Value *m_ptr = ctx.get_w2o_transform_value();

							// point.x * w2o[0].x + point.y * w2o[0].y + point.z * w2o[0].z + w2o[0].w,
							// point.x * w2o[1].x + point.y * w2o[1].y + point.z * w2o[1].z + w2o[1].w,
							// point.x * w2o[2].x + point.y * w2o[2].y + point.z * w2o[2].z + w2o[2].w

							llvm::Value *idx, *ptr, *v;

							res = llvm::Constant::getNullValue(ret_tp);

							llvm::Value *row[3];
							unsigned w[] = { 3 };
							for (int i = 0; i < 3; ++i) {
								idx    = ctx.get_constant(i);
								ptr    = ctx->CreateInBoundsGEP(m_ptr, idx);
								row[i] = ctx->CreateLoad(ptr);
								v      = ctx->CreateExtractValue(row[i], w);
								res    = ctx->CreateInsertElement(res, v, idx);
							}

							for (int i = 2; i >= 0; --i) {
								unsigned idxes[] = { unsigned(i) };
								llvm::Value *t = llvm::Constant::getNullValue(vec_tp);

								v   = ctx->CreateExtractValue(row[0], idxes);
								idx = ctx.get_constant(0);
								t   = ctx->CreateInsertElement(t, v, idx);

								v   = ctx->CreateExtractValue(row[1], idxes);
								idx = ctx.get_constant(1);
								t   = ctx->CreateInsertElement(t, v, idx);

								v   = ctx->CreateExtractValue(row[2], idxes);
								idx = ctx.get_constant(2);
								t   = ctx->CreateInsertElement(t, v, idx);

								idx = ctx.get_constant(i);
								v   = ctx->CreateExtractElement(point, idx);
								v   = ctx.create_vector_splat(vec_tp, v);
								v   = ctx->CreateFMul(v, t);
								res = ctx->CreateFAdd(res, v);
							}
							ctx->CreateStore(res, result);
							ctx->CreateBr(end_bb);
						}
						{
							ctx->SetInsertPoint(o2w_bb);

							llvm::Value *m_ptr = ctx.get_o2w_transform_value();

							// point.x * o2w[0].x + point.y * o2w[0].y + point.z * o2w[0].z + o2w[0].w,
							// point.x * o2w[1].x + point.y * o2w[1].y + point.z * o2w[1].z + o2w[1].w,
							// point.x * o2w[2].x + point.y * o2w[2].y + point.z * o2w[2].z + o2w[2].w

							llvm::Value *idx, *ptr, *v;

							res = llvm::Constant::getNullValue(ret_tp);

							llvm::Value *row[3];
							unsigned w[] = { 3 };
							for (int i = 0; i < 3; ++i) {
								idx    = ctx.get_constant(i);
								ptr    = ctx->CreateInBoundsGEP(m_ptr, idx);
								row[i] = ctx->CreateLoad(ptr);
								v      = ctx->CreateExtractValue(row[i], w);
								res    = ctx->CreateInsertElement(res, v, idx);
							}

							for (int i = 2; i >= 0; --i) {
								unsigned idxes[] = { unsigned(i) };
								llvm::Value *t = llvm::Constant::getNullValue(vec_tp);

								v   = ctx->CreateExtractValue(row[0], idxes);
								idx = ctx.get_constant(0);
								t   = ctx->CreateInsertElement(t, v, idx);

								v   = ctx->CreateExtractValue(row[1], idxes);
								idx = ctx.get_constant(1);
								t   = ctx->CreateInsertElement(t, v, idx);

								v   = ctx->CreateExtractValue(row[2], idxes);
								idx = ctx.get_constant(2);
								t   = ctx->CreateInsertElement(t, v, idx);

								idx = ctx.get_constant(i);
								v   = ctx->CreateExtractElement(point, idx);
								v   = ctx.create_vector_splat(vec_tp, v);
								v   = ctx->CreateFMul(v, t);
								res = ctx->CreateFAdd(res, v);
							}
							ctx->CreateStore(res, result);
							ctx->CreateBr(end_bb);
						}
					} else {
						// scalar mode
						ctx->CreateCondBr(cond, w2o_bb, o2w_bb);
						{
							ctx->SetInsertPoint(w2o_bb);

							llvm::Value *m_ptr = ctx.get_w2o_transform_value();

							// point.x * w2o[0].x + point.y * w2o[0].y + point.z * w2o[0].z + w2o[0].w,
							// point.x * w2o[1].x + point.y * w2o[1].y + point.z * w2o[1].z + w2o[1].w,
							// point.x * w2o[2].x + point.y * w2o[2].y + point.z * w2o[2].z + w2o[2].w

							res = llvm::Constant::getNullValue(ret_tp);

							llvm::Value *idx, *ptr, *v;

							llvm::Value *row[3];
							unsigned w[] = { 3 };
							for (int i = 0; i < 3; ++i) {
								unsigned idxes[] = { unsigned(i) };
								idx    = ctx.get_constant(i);
								ptr    = ctx->CreateInBoundsGEP(m_ptr, idx);
								row[i] = ctx->CreateLoad(ptr);
								v      = ctx->CreateExtractValue(row[i], w);
								res    = ctx->CreateInsertValue(res, v, idxes);
							}

							for (int i = 2; i >= 0; --i) {
								unsigned idxes[] = { unsigned(i) };

								v = ctx->CreateExtractValue(point, idxes);
								for (unsigned j = 0; j < 3; ++j) {
									unsigned comp[] = { j };
									llvm::Value *c = ctx->CreateExtractValue(row[j], idxes);
									llvm::Value *t = ctx->CreateFMul(v, c);
									c = ctx->CreateExtractValue(res, comp);
									t = ctx->CreateFAdd(t, c);
									res = ctx->CreateInsertValue(res, t, comp);
								}
							}
							ctx->CreateStore(res, result);
							ctx->CreateBr(end_bb);
						}
						{
							ctx->SetInsertPoint(o2w_bb);

							llvm::Value *m_ptr = ctx.get_o2w_transform_value();

							// point.x * o2w[0].x + point.y * o2w[0].y + point.z * o2w[0].z + o2w[0].w,
							// point.x * o2w[1].x + point.y * o2w[1].y + point.z * o2w[1].z + o2w[1].w,
							// point.x * o2w[2].x + point.y * o2w[2].y + point.z * o2w[2].z + o2w[2].w

							res = llvm::Constant::getNullValue(ret_tp);

							llvm::Value *idx, *ptr, *v;

							llvm::Value *row[3];
							unsigned w[] = { 3 };
							for (int i = 0; i < 3; ++i) {
								unsigned idxes[] = { unsigned(i) };
								idx    = ctx.get_constant(i);
								ptr    = ctx->CreateInBoundsGEP(m_ptr, idx);
								row[i] = ctx->CreateLoad(ptr);
								v      = ctx->CreateExtractValue(row[i], w);
								res    = ctx->CreateInsertValue(res, v, idxes);
							}

							for (int i = 2; i >= 0; --i) {
								unsigned idxes[] = { unsigned(i) };

								v = ctx->CreateExtractValue(point, idxes);
								for (unsigned j = 0; j < 3; ++j) {
									unsigned comp[] = { j };
									llvm::Value *c = ctx->CreateExtractValue(row[j], idxes);
									llvm::Value *t = ctx->CreateFMul(v, c);
									c = ctx->CreateExtractValue(res, comp);
									t = ctx->CreateFAdd(t, c);
									res = ctx->CreateInsertValue(res, t, comp);
								}
							}
							ctx->CreateStore(res, result);
							ctx->CreateBr(end_bb);
						}
					}
				} else {
					// zero in all other contexts
					ctx->CreateBr(end_bb);
				}
			}
			ctx->SetInsertPoint(end_bb);
			res = ctx->CreateLoad(result);
			"""
			self.format_code(f, code)

		elif mode == "state::transform_vector":
			code = """
			llvm::Type  *ret_tp = ctx_data->get_return_type();
			llvm::Value *from   = a;
			llvm::Value *to     = b;
			llvm::Value *vector = c;

			llvm::Value *internal = ctx.get_constant(LLVM_code_generator::coordinate_internal);
			llvm::Value *encoding = ctx.get_constant(m_internal_space);

			// map internal space
			llvm::Value *f_cond = ctx->CreateICmpEQ(from, internal);
			from = ctx->CreateSelect(f_cond, encoding, from);
			llvm::Value *t_cond = ctx->CreateICmpEQ(to, internal);
			to = ctx->CreateSelect(t_cond, encoding, to);

			res = llvm::Constant::getNullValue(ret_tp);

			llvm::Value *result = ctx.create_local(ret_tp, "result");
			ctx->CreateStore(res, result);

			llvm::Value *cond           = ctx->CreateICmpEQ(from, to);
			llvm::BasicBlock *id_bb     = ctx.create_bb("id");
			llvm::BasicBlock *non_id_bb = ctx.create_bb("non_id");
			llvm::BasicBlock *end_bb    = ctx.create_bb("end");

			ctx->CreateCondBr(cond, id_bb, non_id_bb);
			{
				// the matrix is the identity, return the vector
				ctx->SetInsertPoint(id_bb);

				ctx->CreateStore(vector, result);
				ctx->CreateBr(end_bb);
			}
			{
				ctx->SetInsertPoint(non_id_bb);

				if (m_code_gen.m_state_mode & Type_mapper::SSM_CORE) {
					llvm::Value *worldToObject = ctx.get_constant(LLVM_code_generator::coordinate_world);
					llvm::Value *cond = ctx->CreateICmpEQ(from, worldToObject);

					llvm::BasicBlock *w2o_bb = ctx.create_bb("w2o");
					llvm::BasicBlock *o2w_bb = ctx.create_bb("o2w");

					if (ret_tp->isVectorTy()) {
						// vector mode
						llvm::VectorType *vec_tp = llvm::cast<llvm::VectorType>(ret_tp);

						ctx->CreateCondBr(cond, w2o_bb, o2w_bb);
						{
							ctx->SetInsertPoint(w2o_bb);

							llvm::Value *m_ptr = ctx.get_w2o_transform_value();

							// vector.x * w2o[0].x + vector.y * w2o[0].y + vector.z * w2o[0].z
							// vector.x * w2o[1].x + vector.y * w2o[1].y + vector.z * w2o[1].z
							// vector.x * w2o[2].x + vector.y * w2o[2].y + vector.z * w2o[2].z

							llvm::Value *idx, *ptr, *v;

							llvm::Value *row[3];
							for (int i = 0; i < 3; ++i) {
								idx    = ctx.get_constant(i);
								ptr    = ctx->CreateInBoundsGEP(m_ptr, idx);
								row[i] = ctx->CreateLoad(ptr);
							}

							res = llvm::Constant::getNullValue(ret_tp);
							for (int i = 2; i >= 0; --i) {
								unsigned idxes[] = { unsigned(i) };
								llvm::Value *t = llvm::Constant::getNullValue(vec_tp);

								v   = ctx->CreateExtractValue(row[0], idxes);
								idx = ctx.get_constant(0);
								t   = ctx->CreateInsertElement(t, v, idx);

								v   = ctx->CreateExtractValue(row[1], idxes);
								idx = ctx.get_constant(1);
								t   = ctx->CreateInsertElement(t, v, idx);

								v   = ctx->CreateExtractValue(row[2], idxes);
								idx = ctx.get_constant(2);
								t   = ctx->CreateInsertElement(t, v, idx);

								idx = ctx.get_constant(i);
								v   = ctx->CreateExtractElement(vector, idx);
								v   = ctx.create_vector_splat(vec_tp, v);
								v   = ctx->CreateFMul(v, t);
								res = ctx->CreateFAdd(res, v);
							}
							ctx->CreateStore(res, result);
							ctx->CreateBr(end_bb);
						}
						{
							ctx->SetInsertPoint(o2w_bb);

							llvm::Value *m_ptr = ctx.get_o2w_transform_value();

							// vector.x * o2w[0].x + vector.y * o2w[0].y + vector.z * o2w[0].z
							// vector.x * o2w[1].x + vector.y * o2w[1].y + vector.z * o2w[1].z
							// vector.x * o2w[2].x + vector.y * o2w[2].y + vector.z * o2w[2].z

							llvm::Value *idx, *ptr, *v;

							llvm::Value *row[3];
							for (int i = 0; i < 3; ++i) {
								idx    = ctx.get_constant(i);
								ptr    = ctx->CreateInBoundsGEP(m_ptr, idx);
								row[i] = ctx->CreateLoad(ptr);
							}

							res = llvm::Constant::getNullValue(ret_tp);
							for (int i = 2; i >= 0; --i) {
								unsigned idxes[] = { unsigned(i) };
								llvm::Value *t = llvm::Constant::getNullValue(vec_tp);

								v   = ctx->CreateExtractValue(row[0], idxes);
								idx = ctx.get_constant(0);
								t   = ctx->CreateInsertElement(t, v, idx);

								v   = ctx->CreateExtractValue(row[1], idxes);
								idx = ctx.get_constant(1);
								t   = ctx->CreateInsertElement(t, v, idx);

								v   = ctx->CreateExtractValue(row[2], idxes);
								idx = ctx.get_constant(2);
								t   = ctx->CreateInsertElement(t, v, idx);

								idx = ctx.get_constant(i);
								v   = ctx->CreateExtractElement(vector, idx);
								v   = ctx.create_vector_splat(vec_tp, v);
								v   = ctx->CreateFMul(v, t);
								res = ctx->CreateFAdd(res, v);
							}
							ctx->CreateStore(res, result);
							ctx->CreateBr(end_bb);
						}
					} else {
						// scalar mode
						ctx->CreateCondBr(cond, w2o_bb, o2w_bb);
						{
							ctx->SetInsertPoint(w2o_bb);

							llvm::Value *m_ptr = ctx.get_w2o_transform_value();

							// vector.x * w2o[0].x + vector.y * w2o[0].y + vector.z * w2o[0].z
							// vector.x * w2o[1].x + vector.y * w2o[1].y + vector.z * w2o[1].z
							// vector.x * w2o[2].x + vector.y * w2o[2].y + vector.z * w2o[2].z

							llvm::Value *idx, *ptr, *v;

							llvm::Value *row[3];
							for (int i = 0; i < 3; ++i) {
								idx    = ctx.get_constant(i);
								ptr    = ctx->CreateInBoundsGEP(m_ptr, idx);
								row[i] = ctx->CreateLoad(ptr);
							}

							res = llvm::Constant::getNullValue(ret_tp);
							for (int i = 2; i >= 0; --i) {
								unsigned idxes[] = { unsigned(i) };

								v = ctx->CreateExtractValue(vector, idxes);
								for (unsigned j = 0; j < 3; ++j) {
									unsigned comp[] = { j };
									llvm::Value *c = ctx->CreateExtractValue(row[j], idxes);
									llvm::Value *t = ctx->CreateFMul(v, c);
									c = ctx->CreateExtractValue(res, comp);
									t = ctx->CreateFAdd(t, c);
									res = ctx->CreateInsertValue(res, t, comp);
								}
							}
							ctx->CreateStore(res, result);
							ctx->CreateBr(end_bb);
						}
						{
							ctx->SetInsertPoint(o2w_bb);

							llvm::Value *m_ptr = ctx.get_o2w_transform_value();

							// vector.x * o2w[0].x + vector.y * o2w[0].y + vector.z * o2w[0].z
							// vector.x * o2w[1].x + vector.y * o2w[1].y + vector.z * o2w[1].z
							// vector.x * o2w[2].x + vector.y * o2w[2].y + vector.z * o2w[2].z

							llvm::Value *idx, *ptr, *v;

							llvm::Value *row[3];
							for (int i = 0; i < 3; ++i) {
								idx    = ctx.get_constant(i);
								ptr    = ctx->CreateInBoundsGEP(m_ptr, idx);
								row[i] = ctx->CreateLoad(ptr);
							}

							res = llvm::Constant::getNullValue(ret_tp);
							for (int i = 2; i >= 0; --i) {
								unsigned idxes[] = { unsigned(i) };

								v = ctx->CreateExtractValue(vector, idxes);
								for (unsigned j = 0; j < 3; ++j) {
									unsigned comp[] = { j };
									llvm::Value *c = ctx->CreateExtractValue(row[j], idxes);
									llvm::Value *t = ctx->CreateFMul(v, c);
									c = ctx->CreateExtractValue(res, comp);
									t = ctx->CreateFAdd(t, c);
									res = ctx->CreateInsertValue(res, t, comp);
								}
							}
							ctx->CreateStore(res, result);
							ctx->CreateBr(end_bb);
						}
					}
				} else {
					// zero in all other contexts
					ctx->CreateBr(end_bb);
				}
			}
			ctx->SetInsertPoint(end_bb);
			res = ctx->CreateLoad(result);
			"""
			self.format_code(f, code)

		elif mode == "state::transform_normal":
			code = """
			llvm::Type  *ret_tp = ctx_data->get_return_type();
			llvm::Value *from   = a;
			llvm::Value *to     = b;
			llvm::Value *normal = c;

			llvm::Value *internal = ctx.get_constant(LLVM_code_generator::coordinate_internal);
			llvm::Value *encoding = ctx.get_constant(m_internal_space);

			// map internal space
			llvm::Value *f_cond = ctx->CreateICmpEQ(from, internal);
			from = ctx->CreateSelect(f_cond, encoding, from);
			llvm::Value *t_cond = ctx->CreateICmpEQ(to, internal);
			to = ctx->CreateSelect(t_cond, encoding, to);

			res = llvm::Constant::getNullValue(ret_tp);

			llvm::Value *result = ctx.create_local(ret_tp, "result");
			ctx->CreateStore(res, result);

			llvm::Value *cond           = ctx->CreateICmpEQ(from, to);
			llvm::BasicBlock *id_bb     = ctx.create_bb("id");
			llvm::BasicBlock *non_id_bb = ctx.create_bb("non_id");
			llvm::BasicBlock *end_bb    = ctx.create_bb("end");

			ctx->CreateCondBr(cond, id_bb, non_id_bb);
			{
				// the matrix is the identity, return the normal
				ctx->SetInsertPoint(id_bb);

				ctx->CreateStore(normal, result);
				ctx->CreateBr(end_bb);
			}
			{
				ctx->SetInsertPoint(non_id_bb);

				if (m_code_gen.m_state_mode & Type_mapper::SSM_CORE) {
					llvm::Value *worldToObject = ctx.get_constant(LLVM_code_generator::coordinate_world);
					llvm::Value *cond = ctx->CreateICmpEQ(from, worldToObject);

					llvm::BasicBlock *w2o_bb = ctx.create_bb("w2o");
					llvm::BasicBlock *o2w_bb = ctx.create_bb("o2w");

					if (ret_tp->isVectorTy()) {
						// vector mode
						llvm::VectorType *vec_tp = llvm::cast<llvm::VectorType>(ret_tp);

						ctx->CreateCondBr(cond, w2o_bb, o2w_bb);
						{
							ctx->SetInsertPoint(w2o_bb);

							llvm::Value *m_ptr = ctx.get_o2w_transform_value();

							// normal.x * o2w[0].x + normal.y * o2w[1].x + normal.z * o2w[2].x
							// normal.x * o2w[0].y + normal.y * o2w[1].y + normal.z * o2w[2].y
							// normal.x * o2w[0].z + normal.y * o2w[1].z + normal.z * o2w[2].z

							llvm::Value *idx, *ptr, *row, *v;

							res = llvm::Constant::getNullValue(ret_tp);
							for (int i = 2; i >= 0; --i) {
								idx = ctx.get_constant(i);
								ptr = ctx->CreateInBoundsGEP(m_ptr, idx);
								row = ctx.load_and_convert(vec_tp, ptr);
								v   = ctx->CreateExtractElement(normal, idx);
								v   = ctx.create_vector_splat(vec_tp, v);
								v   = ctx->CreateFMul(v, row);
								res = ctx->CreateFAdd(res, v);
							}
							ctx->CreateStore(res, result);
							ctx->CreateBr(end_bb);
						}
						{
							ctx->SetInsertPoint(o2w_bb);

							llvm::Value *m_ptr = ctx.get_w2o_transform_value();

							// normal.x * w2o[0].x + normal.y * w2o[1].x + normal.z * w2o[2].x
							// normal.x * w2o[0].y + normal.y * w2o[1].y + normal.z * w2o[2].y
							// normal.x * w2o[0].z + normal.y * w2o[1].z + normal.z * w2o[2].z

							llvm::Value *idx, *ptr, *row, *v;

							res = llvm::Constant::getNullValue(ret_tp);
							for (int i = 2; i >= 0; --i) {
								idx = ctx.get_constant(i);
								ptr = ctx->CreateInBoundsGEP(m_ptr, idx);
								row = ctx.load_and_convert(vec_tp, ptr);
								v   = ctx->CreateExtractElement(normal, idx);
								v   = ctx.create_vector_splat(vec_tp, v);
								v   = ctx->CreateFMul(v, row);
								res = ctx->CreateFAdd(res, v);
							}
							ctx->CreateStore(res, result);
							ctx->CreateBr(end_bb);
						}
					} else {
						// scalar mode
						llvm::ArrayType *arr_tp = llvm::cast<llvm::ArrayType>(ret_tp);

						ctx->CreateCondBr(cond, w2o_bb, o2w_bb);
						{
							ctx->SetInsertPoint(w2o_bb);

							llvm::Value *m_ptr = ctx.get_o2w_transform_value();

							// normal.x * o2w[0].x + normal.y * o2w[1].x + normal.z * o2w[2].x
							// normal.x * o2w[0].y + normal.y * o2w[1].y + normal.z * o2w[2].y
							// normal.x * o2w[0].z + normal.y * o2w[1].z + normal.z * o2w[2].z

							llvm::Value *idx, *ptr, *row, *v;

							res = llvm::Constant::getNullValue(ret_tp);
							for (int i = 2; i >= 0; --i) {
								unsigned idxes[] = { unsigned(i) };

								idx = ctx.get_constant(i);
								ptr = ctx->CreateInBoundsGEP(m_ptr, idx);
								row = ctx.load_and_convert(arr_tp, ptr);
								v   = ctx->CreateExtractValue(normal, idxes);

								for (unsigned j = 0; j < 3; ++j) {
									unsigned comp[] = { j };
									llvm::Value *c = ctx->CreateExtractValue(row, comp);
									llvm::Value *t = ctx->CreateFMul(v, c);
									c = ctx->CreateExtractValue(res, comp);
									t = ctx->CreateFAdd(t, c);
									res = ctx->CreateInsertValue(res, t, comp);
								}
							}
							ctx->CreateStore(res, result);
							ctx->CreateBr(end_bb);
						}
						{
							ctx->SetInsertPoint(o2w_bb);

							llvm::Value *m_ptr = ctx.get_w2o_transform_value();

							// normal.x * w2o[0].x + normal.y * w2o[1].x + normal.z * w2o[2].x
							// normal.x * w2o[0].y + normal.y * w2o[1].y + normal.z * w2o[2].y
							// normal.x * w2o[0].z + normal.y * w2o[1].z + normal.z * w2o[2].z

							llvm::Value *idx, *ptr, *row, *v;

							res = llvm::Constant::getNullValue(ret_tp);
							for (int i = 2; i >= 0; --i) {
								unsigned idxes[] = { unsigned(i) };

								idx = ctx.get_constant(i);
								ptr = ctx->CreateInBoundsGEP(m_ptr, idx);
								row = ctx.load_and_convert(arr_tp, ptr);
								v   = ctx->CreateExtractValue(normal, idxes);

								for (unsigned j = 0; j < 3; ++j) {
									unsigned comp[] = { j };
									llvm::Value *c = ctx->CreateExtractValue(row, comp);
									llvm::Value *t = ctx->CreateFMul(v, c);
									c = ctx->CreateExtractValue(res, comp);
									t = ctx->CreateFAdd(t, c);
									res = ctx->CreateInsertValue(res, t, comp);
								}
							}
							ctx->CreateStore(res, result);
							ctx->CreateBr(end_bb);
						}
					}
				} else {
					// zero in all other contexts
					ctx->CreateBr(end_bb);
				}
			}
			ctx->SetInsertPoint(end_bb);
			res = ctx->CreateLoad(result);
			"""
			self.format_code(f, code)

		elif mode == "state::transform_scale":
			code = """
			llvm::Type  *ret_tp = ctx_data->get_return_type();
			llvm::Value *from   = a;
			llvm::Value *to     = b;
			llvm::Value *scale  = c;

			llvm::Value *internal = ctx.get_constant(LLVM_code_generator::coordinate_internal);
			llvm::Value *encoding = ctx.get_constant(m_internal_space);

			// map internal space
			llvm::Value *f_cond = ctx->CreateICmpEQ(from, internal);
			from = ctx->CreateSelect(f_cond, encoding, from);
			llvm::Value *t_cond = ctx->CreateICmpEQ(to, internal);
			to = ctx->CreateSelect(t_cond, encoding, to);

			res = llvm::Constant::getNullValue(ret_tp);

			llvm::Value *result = ctx.create_local(ret_tp, "result");
			ctx->CreateStore(res, result);

			llvm::Value *cond           = ctx->CreateICmpEQ(from, to);
			llvm::BasicBlock *id_bb     = ctx.create_bb("id");
			llvm::BasicBlock *non_id_bb = ctx.create_bb("non_id");
			llvm::BasicBlock *end_bb    = ctx.create_bb("end");

			ctx->CreateCondBr(cond, id_bb, non_id_bb);
			{
				// the matrix is the identity, return the scale
				ctx->SetInsertPoint(id_bb);

				ctx->CreateStore(scale, result);
				ctx->CreateBr(end_bb);
			}
			{
				ctx->SetInsertPoint(non_id_bb);

				if (m_code_gen.m_state_mode & Type_mapper::SSM_CORE) {
					llvm::Value *worldToObject = ctx.get_constant(LLVM_code_generator::coordinate_world);
					llvm::Value *cond = ctx->CreateICmpEQ(from, worldToObject);

					llvm::Value *w2o_ptr = ctx.get_w2o_transform_value();
					llvm::Value *o2w_ptr = ctx.get_o2w_transform_value();
					llvm::Value *m_ptr = ctx->CreateSelect(cond, w2o_ptr, o2w_ptr);

					mi::mdl::IDefinition const *t_def = m_code_gen.find_stdlib_signature("::math", "length(float3)");

					llvm::Function *t_fkt = get_intrinsic_function(t_def);
					llvm::Type *float3_tp = m_code_gen.get_type_mapper().get_float3_type();
					llvm::Value *idx, *ptr;
					llvm::Value *t_args[1];

					// || transform_vector(float3(1,0,0), a, b) || == || transform[0] ||
					idx = ctx.get_constant(0);
					ptr = ctx->CreateInBoundsGEP(m_ptr, idx);
					t_args[0] = ctx.load_and_convert(float3_tp, ptr);
					llvm::Value *v_x = call_rt_func(ctx, t_fkt, t_args);

					// || transform_vector(float3(0,1,0), a, b) || == || transform[1] ||
					idx = ctx.get_constant(1);
					ptr = ctx->CreateInBoundsGEP(m_ptr, idx);
					t_args[0] = ctx.load_and_convert(float3_tp, ptr);
					llvm::Value *v_y = call_rt_func(ctx, t_fkt, t_args);

					// || transform_vector(float3(0,0,1), a, b) || == || transform[2] ||
					idx = ctx.get_constant(2);
					ptr = ctx->CreateInBoundsGEP(m_ptr, idx);
					t_args[0] = ctx.load_and_convert(float3_tp, ptr);
					llvm::Value *v_z = call_rt_func(ctx, t_fkt, t_args);

					// calc average
					res = ctx->CreateFAdd(v_x, v_y);
					res = ctx->CreateFAdd(res, v_z);
					res = ctx->CreateFMul(res, ctx.get_constant(1.0f/3.0f));
					res = ctx->CreateFMul(res, scale);

					ctx->CreateStore(res, result);
					ctx->CreateBr(end_bb);
				} else {
					// zero in all other contexts
					ctx->CreateBr(end_bb);
				}
			}
			ctx->SetInsertPoint(end_bb);
			res = ctx->CreateLoad(result);
			"""
			self.format_code(f, code)

		elif mode == "tex::attr_lookup" or mode ==  "tex::attr_lookup_uvtile":
			# texture attribute
			code_params = {}
			if intrinsic == "width":
				code_params["name"] = "WIDTH"
			elif intrinsic == "height":
				code_params["name"] = "HEIGHT"
			elif intrinsic == "depth":
				code_params["name"]  = "DEPTH"
			elif intrinsic == "texture_isvalid":
				code_params["name"]  = "VALID"

			if mode == "tex::attr_lookup_uvtile":
				code_params["get_uv_tile"] = "ctx.convert_and_store(b, uv_tile);"
			else:
				code_params["get_uv_tile"] = "ctx.store_int2_zero(uv_tile);"

			# check for udim special cases
			texture_param = params[0]
			if texture_param == "T2" and intrinsic in ["width", "height"]:
				# special handling for texture_2d width() and height(), because these have
				# uv_tile extra parameter, use the resource handler or resolution function
				# (i.e. no resource table)
				if intrinsic == "width":
					code_params["res_proj"] = "0"
					code_params["comment_name"] = "width"
				else:
					code_params["res_proj"] = "1"
					code_params["comment_name"] = "height"
				code = """
				if (m_has_res_handler) {
					llvm::Type  *res_type   = m_code_gen.m_type_mapper.get_arr_int_2_type();
					llvm::Type  *coord_type = m_code_gen.m_type_mapper.get_arr_int_2_type();
					llvm::Value *tmp        = ctx.create_local(res_type, "tmp");
					llvm::Value *uv_tile    = ctx.create_local(coord_type, "uv_tile");

					%(get_uv_tile)s
					llvm::Function *glue_func = get_runtime_func(RT_MDL_TEX_RESOLUTION_2D);
					ctx->CreateCall4(glue_func, tmp, res_data, a, uv_tile);

					// return the %(comment_name)s component of the resolution
					llvm::Value *arr = ctx->CreateLoad(tmp);
					unsigned idxs[] = { %(res_proj)s };
					res = ctx->CreateExtractValue(arr, idxs);
				} else {
					llvm::Value *self_adr = ctx.create_simple_gep_in_bounds(
						res_data, ctx.get_constant(Type_mapper::RDP_THREAD_DATA));
					llvm::Value *self     = ctx->CreateBitCast(
						ctx->CreateLoad(self_adr),
						m_code_gen.m_type_mapper.get_core_tex_handler_ptr_type());

					llvm::Value *resolution_func = ctx.get_tex_lookup_func(
						self, Type_mapper::THV_tex_resolution_2d);

					llvm::Type  *res_type   = m_code_gen.m_type_mapper.get_arr_int_2_type();
					llvm::Type  *coord_type = m_code_gen.m_type_mapper.get_arr_int_2_type();
					llvm::Value *tmp        = ctx.create_local(res_type, "tmp");
					llvm::Value *uv_tile    = ctx.create_local(coord_type, "uv_tile");

					%(get_uv_tile)s
					llvm::Value *args[] = { tmp, self, a, uv_tile };
					llvm::CallInst *call = ctx->CreateCall(resolution_func, args);
					call->setDoesNotThrow();

					// return the %(comment_name)s component of the resolution
					llvm::Value *arr = ctx->CreateLoad(tmp);
					unsigned idxs[] = { %(res_proj)s };
					res = ctx->CreateExtractValue(arr, idxs);
				}
				""" % code_params
			else:
				# use resource handler or lookup table
				code = """
				if (m_has_res_handler) {
					llvm::Function *glue_func = get_runtime_func(RT_MDL_TEX_%(name)s);
					res = ctx->CreateCall2(glue_func, res_data, a);
				} else {
					llvm::Type  *res_type = ctx_data->get_return_type();

					llvm::Value *lut      = m_code_gen.get_attribute_table(
						ctx, LLVM_code_generator::RTK_TEXTURE);
					llvm::Value *lut_size = m_code_gen.get_attribute_table_size(
						ctx, LLVM_code_generator::RTK_TEXTURE);
					if (lut != NULL) {
						// have a lookup table
						llvm::Value *tmp  = ctx.create_local(res_type, "tmp");

						llvm::Value *cond = ctx->CreateICmpULT(a, lut_size);

						llvm::BasicBlock *lut_bb = ctx.create_bb("lut_bb");
						llvm::BasicBlock *bad_bb = ctx.create_bb("bad_bb");
						llvm::BasicBlock *end_bb = ctx.create_bb("end");

						// we do not expect out of bounds here
						ctx.CreateWeightedCondBr(cond, lut_bb, bad_bb, 1, 0);
						{
							ctx->SetInsertPoint(lut_bb);

							llvm::Value *select[] = {
								a,
								ctx.get_constant(int(Type_mapper::TAE_%(name)s))
							};

							llvm::Value *adr = ctx->CreateInBoundsGEP(lut, select);
							llvm::Value *v   = ctx->CreateLoad(adr);

							ctx->CreateStore(v, tmp);
							ctx->CreateBr(end_bb);
						}
						{
							ctx->SetInsertPoint(bad_bb);
							ctx->CreateStore(llvm::Constant::getNullValue(res_type), tmp);
							ctx->CreateBr(end_bb);
						}
						{
							ctx->SetInsertPoint(end_bb);
							res = ctx->CreateLoad(tmp);
						}
					} else {
						// no lookup table
						res = llvm::Constant::getNullValue(res_type);
					}
				}
				""" % code_params
			self.format_code(f, code)

		elif mode == "tex::lookup_float":
			# texture lookup for texture
			texture_param = params[0]
			if texture_param == "T2":
				code = """
				if (m_has_res_handler) {
					llvm::Function *lookup_func = get_runtime_func(RT_MDL_TEX_LOOKUP_FLOAT_2D);

					llvm::Type  *f2_type = m_code_gen.m_type_mapper.get_arr_float_2_type();
					llvm::Value *coord   = ctx.create_local(f2_type, "coord");
					llvm::Value *crop_u  = ctx.create_local(f2_type, "crop_u");
					llvm::Value *crop_v  = ctx.create_local(f2_type, "crop_v");

					ctx.convert_and_store(b, coord);
					ctx.convert_and_store(e, crop_u);
					ctx.convert_and_store(f, crop_v);
					llvm::Value *args[] = { res_data, a, coord, c, d, crop_u, crop_v };
					res = ctx->CreateCall(lookup_func, args);
				} else {
					llvm::Value *self_adr = ctx.create_simple_gep_in_bounds(
						res_data, ctx.get_constant(Type_mapper::RDP_THREAD_DATA));
					llvm::Value *self     = ctx->CreateBitCast(
						ctx->CreateLoad(self_adr),
						m_code_gen.m_type_mapper.get_core_tex_handler_ptr_type());

					llvm::Value *lookup_func = ctx.get_tex_lookup_func(
						self, Type_mapper::THV_tex_lookup_float3_2d);

					llvm::Type  *res_type   = m_code_gen.m_type_mapper.get_arr_float_3_type();
					llvm::Type  *coord_type = m_code_gen.m_type_mapper.get_arr_float_2_type();
					llvm::Type  *crop_type  = m_code_gen.m_type_mapper.get_arr_float_2_type();
					llvm::Value *tmp        = ctx.create_local(res_type, "tmp");
					llvm::Value *coord      = ctx.create_local(coord_type, "coord");
					llvm::Value *crop_u     = ctx.create_local(crop_type,  "crop_u");
					llvm::Value *crop_v     = ctx.create_local(crop_type,  "crop_v");

					ctx.convert_and_store(b, coord);
					ctx.convert_and_store(e, crop_u);
					ctx.convert_and_store(f, crop_v);
					llvm::Value *args[] = { tmp, self, a, coord, c, d, crop_u, crop_v };
					llvm::CallInst *call = ctx->CreateCall(lookup_func, args);
					call->setDoesNotThrow();

					// return the first component of the float3 array
					llvm::Value *arr = ctx->CreateLoad(tmp);
					unsigned idxs[] = { 0 };
					res = ctx->CreateExtractValue(arr, idxs);
				}
				"""
			elif texture_param == "T3":
				code = """
				if (m_has_res_handler) {
					llvm::Function *lookup_func = get_runtime_func(RT_MDL_TEX_LOOKUP_FLOAT_3D);

					llvm::Type  *f2_type = m_code_gen.m_type_mapper.get_arr_float_2_type();
					llvm::Type  *f3_type = m_code_gen.m_type_mapper.get_arr_float_3_type();
					llvm::Value *coord   = ctx.create_local(f3_type, "coord");
					llvm::Value *crop_u  = ctx.create_local(f2_type, "crop_u");
					llvm::Value *crop_v  = ctx.create_local(f2_type, "crop_v");
					llvm::Value *crop_w  = ctx.create_local(f2_type, "crop_w");

					ctx.convert_and_store(b, coord);
					ctx.convert_and_store(f, crop_u);
					ctx.convert_and_store(g, crop_v);
					ctx.convert_and_store(h, crop_w);
					llvm::Value *args[] = { res_data, a, coord, c, d, e, crop_u, crop_v, crop_w };
					res = ctx->CreateCall(lookup_func, args);
				} else {
					llvm::Value *self_adr = ctx.create_simple_gep_in_bounds(
						res_data, ctx.get_constant(Type_mapper::RDP_THREAD_DATA));
					llvm::Value *self     = ctx->CreateBitCast(
						ctx->CreateLoad(self_adr),
						m_code_gen.m_type_mapper.get_core_tex_handler_ptr_type());

					llvm::Value *lookup_func = ctx.get_tex_lookup_func(
						self, Type_mapper::THV_tex_lookup_float3_3d);

					llvm::Type  *res_type   = m_code_gen.m_type_mapper.get_arr_float_3_type();
					llvm::Type  *coord_type = m_code_gen.m_type_mapper.get_arr_float_3_type();
					llvm::Type  *crop_type  = m_code_gen.m_type_mapper.get_arr_float_2_type();
					llvm::Value *tmp        = ctx.create_local(res_type, "tmp");
					llvm::Value *coord      = ctx.create_local(coord_type, "coord");
					llvm::Value *crop_u     = ctx.create_local(crop_type,  "crop_u");
					llvm::Value *crop_v     = ctx.create_local(crop_type,  "crop_v");
					llvm::Value *crop_w     = ctx.create_local(crop_type,  "crop_w");

					ctx.convert_and_store(b, coord);
					ctx.convert_and_store(f, crop_u);
					ctx.convert_and_store(g, crop_v);
					ctx.convert_and_store(h, crop_w);
					llvm::Value *args[] = { tmp, self, a, coord, c, d, e, crop_u, crop_v, crop_w };
					llvm::CallInst *call = ctx->CreateCall(lookup_func, args);
					call->setDoesNotThrow();

					// return the first component of the float3 array
					llvm::Value *arr = ctx->CreateLoad(tmp);
					unsigned idxs[] = { 0 };
					res = ctx->CreateExtractValue(arr, idxs);
				}
				"""
			elif texture_param == "TC":
				code = """
				if (m_has_res_handler) {
					llvm::Function *lookup_func = get_runtime_func(RT_MDL_TEX_LOOKUP_FLOAT_CUBE);

					llvm::Type  *f3_type = m_code_gen.m_type_mapper.get_arr_float_3_type();
					llvm::Value *coord   = ctx.create_local(f3_type, "coord");

					ctx.convert_and_store(b, coord);
					llvm::Value *args[] = { res_data, a, coord };
					res = ctx->CreateCall(lookup_func, args);
				} else {
					llvm::Value *self_adr = ctx.create_simple_gep_in_bounds(
						res_data, ctx.get_constant(Type_mapper::RDP_THREAD_DATA));
					llvm::Value *self     = ctx->CreateBitCast(
						ctx->CreateLoad(self_adr),
						m_code_gen.m_type_mapper.get_core_tex_handler_ptr_type());

					llvm::Value *lookup_func = ctx.get_tex_lookup_func(
						self, Type_mapper::THV_tex_lookup_float3_cube);

					llvm::Type  *res_type   = m_code_gen.m_type_mapper.get_arr_float_3_type();
					llvm::Type  *coord_type = m_code_gen.m_type_mapper.get_arr_float_3_type();
					llvm::Value *tmp        = ctx.create_local(res_type, "tmp");
					llvm::Value *coord      = ctx.create_local(coord_type, "coord");

					ctx.convert_and_store(b, coord);
					llvm::Value *args[] = { tmp, self, a, coord };
					llvm::CallInst *call = ctx->CreateCall(lookup_func, args);
					call->setDoesNotThrow();

					// return the first component of the float3 array
					llvm::Value *arr = ctx->CreateLoad(tmp);
					unsigned idxs[] = { 0 };
					res = ctx->CreateExtractValue(arr, idxs);
				}
				"""
			elif texture_param == "TP":
				code = """
				if (m_has_res_handler) {
					llvm::Function *lookup_func = get_runtime_func(RT_MDL_TEX_LOOKUP_FLOAT_PTEX);

					llvm::Value *args[] = { res_data, a, b };
					res = ctx->CreateCall(lookup_func, args);
				} else {
					res = llvm::Constant::getNullValue(ctx_data->get_return_type());
				}
				"""
			else:
				error("Unsupported texture type")
				code = ""
			self.format_code(f, code)

		elif mode == "tex::lookup_floatX":
			# texture lookup_floatX()
			code_params = {"core_th" : "false", "vt_size" : "0" }
			if intrinsic == "lookup_float2":
				code_params["size"] = "2"
				code_params["func"] = "LOOKUP_FLOAT2"
				code_params["vt_size"]  = "3"
			elif intrinsic == "lookup_float3":
				code_params["size"] = "3"
				code_params["func"] = "LOOKUP_FLOAT3"
				code_params["vt_size"]  = "3"
			elif intrinsic == "lookup_float4":
				code_params["size"] = "4"
				code_params["func"] = "LOOKUP_FLOAT4"
				code_params["vt_size"]  = "4"
			elif intrinsic == "lookup_color":
				code_params["size"] = "3"
				code_params["func"] = "LOOKUP_COLOR"
				code_params["vt_size"]  = "3"
			else:
				error("Unsupported tex lookup function '%s'" % intrinsic)

			texture_param = params[0]
			if texture_param == "T2":
				code = """
				if (m_has_res_handler) {
					llvm::Function *lookup_func = get_runtime_func(RT_MDL_TEX_%(func)s_2D);

					llvm::Type  *res_type   = m_code_gen.m_type_mapper.get_arr_float_%(size)s_type();
					llvm::Type  *coord_type = m_code_gen.m_type_mapper.get_arr_float_2_type();
					llvm::Type  *crop_type  = m_code_gen.m_type_mapper.get_arr_float_2_type();
					llvm::Value *tmp        = ctx.create_local(res_type, "tmp");
					llvm::Value *coord      = ctx.create_local(coord_type, "coord");
					llvm::Value *crop_u     = ctx.create_local(crop_type,  "crop_u");
					llvm::Value *crop_v     = ctx.create_local(crop_type,  "crop_v");

					ctx.convert_and_store(b, coord);
					ctx.convert_and_store(e, crop_u);
					ctx.convert_and_store(f, crop_v);
					llvm::Value *args[] = { tmp, res_data, a, coord, c, d, crop_u, crop_v };
					ctx->CreateCall(lookup_func, args);

					res = ctx.load_and_convert(ctx_data->get_return_type(), tmp);
				} else {
					llvm::Value *self_adr = ctx.create_simple_gep_in_bounds(
						res_data, ctx.get_constant(Type_mapper::RDP_THREAD_DATA));
					llvm::Value *self     = ctx->CreateBitCast(
						ctx->CreateLoad(self_adr),
						m_code_gen.m_type_mapper.get_core_tex_handler_ptr_type());

					llvm::Value *lookup_func = ctx.get_tex_lookup_func(
						self, Type_mapper::THV_tex_lookup_float%(vt_size)s_2d);

					llvm::Type  *res_type   = m_code_gen.m_type_mapper.get_arr_float_%(vt_size)s_type();
					llvm::Type  *coord_type = m_code_gen.m_type_mapper.get_arr_float_2_type();
					llvm::Type  *crop_type  = m_code_gen.m_type_mapper.get_arr_float_2_type();
					llvm::Value *tmp        = ctx.create_local(res_type, "tmp");
					llvm::Value *coord      = ctx.create_local(coord_type, "coord");
					llvm::Value *crop_u     = ctx.create_local(crop_type,  "crop_u");
					llvm::Value *crop_v     = ctx.create_local(crop_type,  "crop_v");

					ctx.convert_and_store(b, coord);
					ctx.convert_and_store(e, crop_u);
					ctx.convert_and_store(f, crop_v);
					llvm::Value *args[] = { tmp, self, a, coord, c, d, crop_u, crop_v };
					llvm::CallInst *call = ctx->CreateCall(lookup_func, args);
					call->setDoesNotThrow();

					res = ctx.load_and_convert(ctx_data->get_return_type(), tmp);
				}
				"""
			elif texture_param == "T3":
				code = """
				if (m_has_res_handler) {
					llvm::Function *lookup_func = get_runtime_func(RT_MDL_TEX_%(func)s_3D);

					llvm::Type  *res_type   = m_code_gen.m_type_mapper.get_arr_float_%(size)s_type();
					llvm::Type  *coord_type = m_code_gen.m_type_mapper.get_arr_float_3_type();
					llvm::Type  *crop_type  = m_code_gen.m_type_mapper.get_arr_float_2_type();
					llvm::Value *tmp        = ctx.create_local(res_type, "tmp");
					llvm::Value *coord      = ctx.create_local(coord_type, "coord");
					llvm::Value *crop_u     = ctx.create_local(crop_type, "crop_u");
					llvm::Value *crop_v     = ctx.create_local(crop_type, "crop_v");
					llvm::Value *crop_w     = ctx.create_local(crop_type, "crop_w");

					ctx.convert_and_store(b, coord);
					ctx.convert_and_store(f, crop_u);
					ctx.convert_and_store(g, crop_v);
					ctx.convert_and_store(h, crop_w);
					llvm::Value *args[] = { tmp, res_data, a, coord, c, d, e, crop_u, crop_v, crop_w };
					ctx->CreateCall(lookup_func, args);

					res = ctx.load_and_convert(ctx_data->get_return_type(), tmp);
				} else {
					llvm::Value *self_adr = ctx.create_simple_gep_in_bounds(
						res_data, ctx.get_constant(Type_mapper::RDP_THREAD_DATA));
					llvm::Value *self     = ctx->CreateBitCast(
						ctx->CreateLoad(self_adr),
						m_code_gen.m_type_mapper.get_core_tex_handler_ptr_type());

					llvm::Value *lookup_func = ctx.get_tex_lookup_func(
						self, Type_mapper::THV_tex_lookup_float%(vt_size)s_3d);

					llvm::Type  *res_type   = m_code_gen.m_type_mapper.get_arr_float_%(vt_size)s_type();
					llvm::Type  *coord_type = m_code_gen.m_type_mapper.get_arr_float_3_type();
					llvm::Type  *crop_type  = m_code_gen.m_type_mapper.get_arr_float_2_type();
					llvm::Value *tmp        = ctx.create_local(res_type, "tmp");
					llvm::Value *coord      = ctx.create_local(coord_type, "coord");
					llvm::Value *crop_u     = ctx.create_local(crop_type,  "crop_u");
					llvm::Value *crop_v     = ctx.create_local(crop_type,  "crop_v");
					llvm::Value *crop_w     = ctx.create_local(crop_type,  "crop_w");

					ctx.convert_and_store(b, coord);
					ctx.convert_and_store(f, crop_u);
					ctx.convert_and_store(g, crop_v);
					ctx.convert_and_store(h, crop_w);
					llvm::Value *args[] = { tmp, self, a, coord, c, d, e, crop_u, crop_v, crop_w };
					llvm::CallInst *call = ctx->CreateCall(lookup_func, args);
					call->setDoesNotThrow();

					res = ctx.load_and_convert(ctx_data->get_return_type(), tmp);
				}
				"""
			elif texture_param == "TC":
				code = """
				if (m_has_res_handler) {
					llvm::Function *lookup_func = get_runtime_func(RT_MDL_TEX_%(func)s_CUBE);

					llvm::Type  *res_type   = m_code_gen.m_type_mapper.get_arr_float_%(size)s_type();
					llvm::Type  *coord_type = m_code_gen.m_type_mapper.get_arr_float_3_type();
					llvm::Value *tmp        = ctx.create_local(res_type, "tmp");
					llvm::Value *coord      = ctx.create_local(coord_type, "coord");

					ctx.convert_and_store(b, coord);
					llvm::Value *args[] = { tmp, res_data, a, coord };
					ctx->CreateCall(lookup_func, args);

					res = ctx.load_and_convert(ctx_data->get_return_type(), tmp);
				} else {
					llvm::Value *self_adr = ctx.create_simple_gep_in_bounds(
						res_data, ctx.get_constant(Type_mapper::RDP_THREAD_DATA));
					llvm::Value *self     = ctx->CreateBitCast(
						ctx->CreateLoad(self_adr),
						m_code_gen.m_type_mapper.get_core_tex_handler_ptr_type());

					llvm::Value *lookup_func = ctx.get_tex_lookup_func(
						self, Type_mapper::THV_tex_lookup_float%(vt_size)s_cube);

					llvm::Type  *res_type   = m_code_gen.m_type_mapper.get_arr_float_%(vt_size)s_type();
					llvm::Type  *coord_type = m_code_gen.m_type_mapper.get_arr_float_3_type();
					llvm::Value *tmp        = ctx.create_local(res_type, "tmp");
					llvm::Value *coord      = ctx.create_local(coord_type, "coord");

					ctx.convert_and_store(b, coord);
					llvm::Value *args[] = { tmp, self, a, coord };
					llvm::CallInst *call = ctx->CreateCall(lookup_func, args);
					call->setDoesNotThrow();

					res = ctx.load_and_convert(ctx_data->get_return_type(), tmp);
				}
				"""
			elif texture_param == "TP":
				code = """
				if (m_has_res_handler) {
					llvm::Function *lookup_func = get_runtime_func(RT_MDL_TEX_%(func)s_PTEX);

					llvm::Type  *res_type = m_code_gen.m_type_mapper.get_arr_float_%(size)s_type();
					llvm::Value *tmp      = ctx.create_local(res_type, "tmp");

					llvm::Value *args[] = { tmp, res_data, a, b };
					ctx->CreateCall(lookup_func, args);

					res = ctx.load_and_convert(ctx_data->get_return_type(), tmp);
				} else {
					res = llvm::Constant::getNullValue(ctx_data->get_return_type());
				}
				"""
			else:
				error("Unsupported texture type")
				code = ""
			self.format_code(f, code % code_params)

		elif mode == "tex::texel_float" or mode == "tex::texel_float_uvtile":
			# texture lookup_float()
			code_params = {}
			if mode == "tex::texel_float_uvtile":
				code_params["get_uv_tile"] = "ctx.convert_and_store(c, uv_tile);"
			else:
				code_params["get_uv_tile"] = "ctx.store_int2_zero(uv_tile);"

			texture_param = params[0]
			if texture_param == "T2":
				code = """
				if (m_has_res_handler) {
					llvm::Function *lookup_func = get_runtime_func(RT_MDL_TEX_TEXEL_FLOAT_2D);

					llvm::Type  *coord_type = m_code_gen.m_type_mapper.get_arr_int_2_type();
					llvm::Value *coord      = ctx.create_local(coord_type, "coord");
					llvm::Value *uv_tile    = ctx.create_local(coord_type, "uv_tile");

					ctx.convert_and_store(b, coord);
					%(get_uv_tile)s
					llvm::Value *args[] = { res_data, a, coord, uv_tile };
					res = ctx->CreateCall(lookup_func, args);
				} else {
					llvm::Value *self_adr = ctx.create_simple_gep_in_bounds(
						res_data, ctx.get_constant(Type_mapper::RDP_THREAD_DATA));
					llvm::Value *self     = ctx->CreateBitCast(
						ctx->CreateLoad(self_adr),
						m_code_gen.m_type_mapper.get_core_tex_handler_ptr_type());

					llvm::Value *texel_func = ctx.get_tex_lookup_func(
						self, Type_mapper::THV_tex_texel_float4_2d);

					llvm::Type  *res_type   = m_code_gen.m_type_mapper.get_arr_float_4_type();
					llvm::Type  *coord_type = m_code_gen.m_type_mapper.get_arr_int_2_type();
					llvm::Value *tmp        = ctx.create_local(res_type, "tmp");
					llvm::Value *coord      = ctx.create_local(coord_type, "coord");
					llvm::Value *uv_tile    = ctx.create_local(coord_type, "uv_tile");

					ctx.convert_and_store(b, coord);
					%(get_uv_tile)s
					llvm::Value *args[] = { tmp, self, a, coord, uv_tile };
					llvm::CallInst *call = ctx->CreateCall(texel_func, args);
					call->setDoesNotThrow();

					// return the first component of the float4 array
					llvm::Value *arr = ctx->CreateLoad(tmp);
					unsigned idxs[] = { 0 };
					res = ctx->CreateExtractValue(arr, idxs);
				}
				"""
			elif texture_param == "T3":
				code = """
				if (m_has_res_handler) {
					llvm::Function *lookup_func = get_runtime_func(RT_MDL_TEX_TEXEL_FLOAT_3D);

					llvm::Type  *coord_type = m_code_gen.m_type_mapper.get_arr_int_3_type();
					llvm::Value *coord      = ctx.create_local(coord_type, "coord");

					ctx.convert_and_store(b, coord);
					llvm::Value *args[] = { res_data, a, coord };
					res = ctx->CreateCall(lookup_func, args);
				} else {
					llvm::Value *self_adr = ctx.create_simple_gep_in_bounds(
						res_data, ctx.get_constant(Type_mapper::RDP_THREAD_DATA));
					llvm::Value *self     = ctx->CreateBitCast(
						ctx->CreateLoad(self_adr),
						m_code_gen.m_type_mapper.get_core_tex_handler_ptr_type());

					llvm::Value *texel_func = ctx.get_tex_lookup_func(
						self, Type_mapper::THV_tex_texel_float4_3d);

					llvm::Type  *res_type   = m_code_gen.m_type_mapper.get_arr_float_4_type();
					llvm::Type  *coord_type = m_code_gen.m_type_mapper.get_arr_int_3_type();
					llvm::Value *tmp        = ctx.create_local(res_type, "tmp");
					llvm::Value *coord      = ctx.create_local(coord_type, "coord");

					ctx.convert_and_store(b, coord);
					llvm::Value *args[] = { tmp, self, a, coord };
					llvm::CallInst *call = ctx->CreateCall(texel_func, args);
					call->setDoesNotThrow();

					// return the first component of the float4 array
					llvm::Value *arr = ctx->CreateLoad(tmp);
					unsigned idxs[] = { 0 };
					res = ctx->CreateExtractValue(arr, idxs);
				}
				"""
			else:
				error("Unsupported texture type")
				return
			self.format_code(f, code % code_params)

		elif mode == "tex::texel_floatX" or mode == "tex::texel_floatX_uvtile":
			# texture lookup_floatX()
			code_params = {}
			if intrinsic == "texel_float2":
				code_params["size"] = "2"
				code_params["func"] = "TEXEL_FLOAT2"
			elif intrinsic == "texel_float3":
				code_params["size"] = "3"
				code_params["func"] = "TEXEL_FLOAT3"
			elif intrinsic == "texel_float4":
				code_params["size"] = "4"
				code_params["func"] = "TEXEL_FLOAT4"
			elif intrinsic == "texel_color":
				code_params["size"] = "3"
				code_params["func"] = "TEXEL_COLOR"
			else:
				error("Unsupported tex texel function '%s'" % intrinsic)

			if mode == "tex::texel_floatX_uvtile":
				code_params["get_uv_tile"] = "ctx.convert_and_store(c, uv_tile);"
			else:
				code_params["get_uv_tile"] = "ctx.store_int2_zero(uv_tile);"

			texture_param = params[0]
			if texture_param == "T2":
				code = """
				if (m_has_res_handler) {
					llvm::Function *lookup_func = get_runtime_func(RT_MDL_TEX_%(func)s_2D);

					llvm::Type  *res_type   = m_code_gen.m_type_mapper.get_arr_float_%(size)s_type();
					llvm::Type  *coord_type = m_code_gen.m_type_mapper.get_arr_int_2_type();
					llvm::Value *tmp        = ctx.create_local(res_type, "tmp");
					llvm::Value *coord      = ctx.create_local(coord_type, "coord");
					llvm::Value *uv_tile    = ctx.create_local(coord_type, "uv_tile");

					ctx.convert_and_store(b, coord);
					%(get_uv_tile)s
					llvm::Value *args[] = { tmp, res_data, a, coord, uv_tile };
					ctx->CreateCall(lookup_func, args);
					res = ctx.load_and_convert(ctx_data->get_return_type(), tmp);
				} else {
					llvm::Value *self_adr = ctx.create_simple_gep_in_bounds(
						res_data, ctx.get_constant(Type_mapper::RDP_THREAD_DATA));
					llvm::Value *self     = ctx->CreateBitCast(
						ctx->CreateLoad(self_adr),
						m_code_gen.m_type_mapper.get_core_tex_handler_ptr_type());

					llvm::Value *texel_func = ctx.get_tex_lookup_func(
						self, Type_mapper::THV_tex_texel_float4_2d);

					llvm::Type  *res_type   = m_code_gen.m_type_mapper.get_arr_float_4_type();
					llvm::Type  *coord_type = m_code_gen.m_type_mapper.get_arr_int_2_type();
					llvm::Value *tmp        = ctx.create_local(res_type, "tmp");
					llvm::Value *coord      = ctx.create_local(coord_type, "coord");
					llvm::Value *uv_tile    = ctx.create_local(coord_type, "uv_tile");

					ctx.convert_and_store(b, coord);
					%(get_uv_tile)s
					llvm::Value *args[] = { tmp, self, a, coord, uv_tile };
					llvm::CallInst *call = ctx->CreateCall(texel_func, args);
					call->setDoesNotThrow();

					res = ctx.load_and_convert(ctx_data->get_return_type(), tmp);
				}
				"""
			elif texture_param == "T3":
				code = """
				if (m_has_res_handler) {
					llvm::Function *lookup_func = get_runtime_func(RT_MDL_TEX_%(func)s_3D);

					llvm::Type  *res_type   = m_code_gen.m_type_mapper.get_arr_float_%(size)s_type();
					llvm::Type  *coord_type = m_code_gen.m_type_mapper.get_arr_int_3_type();
					llvm::Value *tmp        = ctx.create_local(res_type, "tmp");
					llvm::Value *coord      = ctx.create_local(coord_type, "coord");

					ctx.convert_and_store(b, coord);
					llvm::Value *args[] = { tmp, res_data, a, coord };
					ctx->CreateCall(lookup_func, args);
					res = ctx.load_and_convert(ctx_data->get_return_type(), tmp);
				} else {
					llvm::Value *self_adr = ctx.create_simple_gep_in_bounds(
						res_data, ctx.get_constant(Type_mapper::RDP_THREAD_DATA));
					llvm::Value *self     = ctx->CreateBitCast(
						ctx->CreateLoad(self_adr),
						m_code_gen.m_type_mapper.get_core_tex_handler_ptr_type());

					llvm::Value *texel_func = ctx.get_tex_lookup_func(
						self, Type_mapper::THV_tex_texel_float4_3d);

					llvm::Type  *res_type   = m_code_gen.m_type_mapper.get_arr_float_4_type();
					llvm::Type  *coord_type = m_code_gen.m_type_mapper.get_arr_int_3_type();
					llvm::Value *tmp        = ctx.create_local(res_type, "tmp");
					llvm::Value *coord      = ctx.create_local(coord_type, "coord");

					ctx.convert_and_store(b, coord);
					llvm::Value *args[] = { tmp, self, a, coord };
					llvm::CallInst *call = ctx->CreateCall(texel_func, args);
					call->setDoesNotThrow();

					res = ctx.load_and_convert(ctx_data->get_return_type(), tmp);
				}
				"""
			else:
				error("Unsupported texture type")
				return

			self.format_code(f, code % code_params)

		elif mode == "debug::breakpoint":
			code = """
			if (m_ptx_mode) {
				llvm::FunctionType *f_tp = llvm::FunctionType::get(
					m_code_gen.m_type_mapper.get_void_type(), /*is_VarArg=*/false);
				llvm::InlineAsm *ia = llvm::InlineAsm::get(
					f_tp,
					"brkpt;",
					"",
					/*hasSideEffects=*/false);
				ctx->CreateCall(ia);
			} else {
				llvm::Function *break_func = get_runtime_func(RT_MDL_DEBUGBREAK);
				ctx->CreateCall(break_func);
			}
			res = ctx.get_constant(true);
			"""
			self.format_code(f, code)

		elif mode == "debug::assert":
			code = """
			llvm::Function   *conv_func = get_runtime_func(RT_MDL_TO_CSTRING);

			llvm::Value      *cond    = ctx->CreateICmpNE(a, ctx.get_constant(false));

			llvm::BasicBlock *fail_bb = ctx.create_bb("fail_bb");
			llvm::BasicBlock *end_bb  = ctx.create_bb("end");

			// we do not expect the assertion to fail here
			ctx.CreateWeightedCondBr(cond, end_bb, fail_bb, 1, 0);
			{
				ctx->SetInsertPoint(fail_bb);

				// convert the string arguments to cstrings
				b = ctx->CreateCall(conv_func, b);  // message
				c = ctx->CreateCall(conv_func, c);  // function name
				d = ctx->CreateCall(conv_func, d);  // file

				if (m_ptx_mode) {
					llvm::Value *args[] = {
						b,                           // message
						d,                           // file
						e,                           // line
						c,                           // function name
						ctx.get_constant(size_t(1))  // charSize
					};
					llvm::Function *assert_func = get_runtime_func(RT___ASSERTFAIL);
					ctx->CreateCall(assert_func, args);
				} else {
					llvm::Value *args[] = {
						b,                           // message
						c,                           // function name
						d,                           // file
						e                            // line
					};
					llvm::Function *assert_func = get_runtime_func(RT_MDL_ASSERTFAIL);
					ctx->CreateCall(assert_func, args);
				}

				ctx->CreateBr(end_bb);
			}
			{
				ctx->SetInsertPoint(end_bb);
			}
			res = ctx.get_constant(true);
			"""
			self.format_code(f, code)

		elif mode == "debug::print":
			# conversion from id to C-string
			conv_from_string_id = """
				llvm::Function *conv_func = get_runtime_func(RT_MDL_TO_CSTRING);
				%(what)s = ctx->CreateCall(conv_func, %(what)s);
			"""

			# PTX prolog
			code = """
				if (m_ptx_mode) {
					llvm::Function    *vprintf_func = get_runtime_func(RT_VPRINTF);
					llvm::PointerType *void_ptr_tp = m_code_gen.m_type_mapper.get_void_ptr_type();
					llvm::DataLayout   data_layout(m_code_gen.get_llvm_module());
					llvm::Twine        format_str;
					int                buffer_size = 0;
					llvm::Type        *operand_type;
			"""
			self.format_code(f, code)

			# Determine buffer size for valist, argument types and format string
			arg_types = []
			format_str = ""

			for param in params:
				atomic_chk = self.get_atomic_type_kind(param)
				vector_chk = self.get_vector_type_and_size(param)

				if param == "CC":  # color
					format_str += "(%s)" % ', '.join(["%f"] * vector_chk[1])
					arg_type = "m_code_gen.m_type_mapper.get_double_type()"
				elif atomic_chk:
					if param == "BB":
						format_str += "%s"
						arg_type = "m_code_gen.m_type_mapper.get_cstring_type()"
					elif param == "II":
						format_str += "%i"
						arg_type = "m_code_gen.m_type_mapper.get_int_type()"
					elif param == "FF":
						format_str += "%f"
						arg_type = "m_code_gen.m_type_mapper.get_double_type()"
					elif param == "DD":
						format_str += "%f"
						arg_type = "m_code_gen.m_type_mapper.get_double_type()"
					elif param == "SS":
						format_str += "%s"
						arg_type = "m_code_gen.m_type_mapper.get_cstring_type()"
					else:
						error("Unsupported print type '%s'" % param)
					code = """
						get_next_valist_entry_offset(buffer_size, %s);
					""" % arg_type
					self.format_code(f, code)
				elif vector_chk:
					size = vector_chk[1]
					if vector_chk[0] == "bool":
						elem_format = "%s"
						arg_type = "m_code_gen.m_type_mapper.get_cstring_type()"
					elif vector_chk[0] == "int":
						elem_format = "%i"
						arg_type = "m_code_gen.m_type_mapper.get_int_type()"
					elif vector_chk[0] == "float":
						elem_format = "%f"
						arg_type = "m_code_gen.m_type_mapper.get_double_type()"
					elif vector_chk[0] == "double":
						elem_format = "%f"
						arg_type = "m_code_gen.m_type_mapper.get_double_type()"
					else:
						error("Unsupported print type '%s'" % param)
					format_str += "<%s>" % ', '.join([elem_format] * vector_chk[1])
					code = """
						operand_type = %(arg_type)s;
						for (unsigned i = 0; i < %(size)d; ++i) {
							get_next_valist_entry_offset(buffer_size, operand_type);
						}
					""" % { "arg_type" : arg_type, "size" : size }
					self.format_code(f, code)
				else:
					error("Unsupported debug::print() parameter type '%s'" % param)

				arg_types.append((arg_type, vector_chk[1] if vector_chk else 1))

			# Allocate valist buffer
			code = """
				buffer_size = data_layout.RoundUpAlignment(buffer_size, VPRINTF_BUFFER_ROUND_UP);
				llvm::AllocaInst *valist = ctx->CreateAlloca(
					llvm::ArrayType::get(
						m_code_gen.m_type_mapper.get_char_type(),
						buffer_size
					),
					NULL,
					"vprintf.valist");
				valist->setAlignment(VPRINTF_BUFFER_ALIGNMENT);

				int offset = 0;
				llvm::Value *elem;
				llvm::Value *pointer;

			"""
			self.format_code(f, code)

			# Fill valist buffer
			idx = 0
			for param in params:
				self.format_code(f, "operand_type = %s;" % arg_types[idx][0])

				# For color and float types, we need to cast the value to double
				if param[0] in ['C', 'F']:
					optcast = """
						elem = ctx->CreateFPExt(elem,
						m_code_gen.m_type_mapper.get_double_type());
					"""
				# For bool types we need to convert it to "true" or "false"
				elif param[0] == 'B':
					optcast = """
						elem = ctx->CreateICmpNE(elem, ctx.get_constant(false));
						elem = ctx->CreateSelect(
							elem, ctx.get_constant("true"), ctx.get_constant("false"));
					"""
				elif param == 'SS':
					optcast = conv_from_string_id % { "what" : "elem" }
				else:
					optcast = ""

				size = arg_types[idx][1]
				if size > 1:
					code = """
						if (llvm::isa<llvm::ArrayType>(%(param)s->getType())) {
							unsigned idxes[1];
							for (unsigned i = 0; i < %(size)d; ++i) {
								idxes[0] = i;
								elem = ctx->CreateExtractValue(%(param)s, idxes);
								%(optcast)s
								pointer = get_next_valist_pointer(ctx, valist,
									offset, operand_type);
								ctx->CreateStore(elem, pointer);
							}
						} else {
							for (int i = 0; i < %(size)d; ++i) {
								llvm::Value *idx  = ctx.get_constant(i);
								elem = ctx->CreateExtractElement(%(param)s, idx);
								%(optcast)s
								pointer = get_next_valist_pointer(ctx, valist,
									offset, operand_type);
								ctx->CreateStore(elem, pointer);
							}
						}

					""" % { "size" : size, "param" : chr(ord('a') + idx), "optcast" : optcast }
				else:
					code = """
						elem = %(param)s;
						%(optcast)s
						pointer = get_next_valist_pointer(ctx, valist, offset, operand_type);
						ctx->CreateStore(elem, pointer);

					""" % { "param" : chr(ord('a') + idx), "optcast" : optcast }
				self.format_code(f, code)
				idx = idx + 1

			# PTX epilog and CPU prolog

			code = """
					llvm::Value *args[] = {
						ctx.get_constant("%s"),
						ctx->CreateBitCast(valist, void_ptr_tp)
					};
					ctx->CreateCall(vprintf_func, args);
				} else {
					llvm::Function *begin_func = get_runtime_func(RT_MDL_PRINT_BEGIN);
					llvm::Value    *buf        = ctx->CreateCall(begin_func);
			""" % format_str
			self.format_code(f, code)

			idx = 0
			for param in params:
				type = ""
				size = 0
				atomic_chk = self.get_atomic_type_kind(param)
				vector_chk = self.get_vector_type_and_size(param)
				if param == "CC":
					# color
					code = """
					{
						llvm::Function *print_func  = get_runtime_func(RT_MDL_PRINT_FLOAT);
						llvm::Function *prints_func = get_runtime_func(RT_MDL_PRINT_STRING);
						llvm::Type     *arg_tp      = %(param)s->getType();

						llvm::Value *comma = ctx.get_constant("(");
						llvm::Value *next  = ctx.get_constant(", ");
						if (llvm::isa<llvm::ArrayType>(arg_tp)) {
							unsigned idxes[1];

							for (unsigned i = 0; i < 3; ++i) {
								ctx->CreateCall2(prints_func, buf, comma);
								comma = next;
								idxes[0] = i;

								llvm::Value *elem = ctx->CreateExtractValue(%(param)s, idxes);
								ctx->CreateCall2(print_func, buf, elem);
							}
						} else {
							for (int i = 0; i < 3; ++i) {
								ctx->CreateCall2(prints_func, buf, comma);
								comma = next;

								llvm::Value *idx  = ctx.get_constant(i);
								llvm::Value *elem = ctx->CreateExtractElement(%(param)s, idx);
								ctx->CreateCall2(print_func, buf, elem);
							}
						}
						llvm::Value *end = ctx.get_constant(")");
						ctx->CreateCall2(prints_func, buf, end);
					}
					"""
				elif atomic_chk:
					add_conv = ""
					type = ""
					if param == "BB":
						type = "BOOL"
					elif param == "II":
						type = "INT"
					elif param == "FF":
						type = "FLOAT"
					elif param == "DD":
						type = "DOUBLE"
					elif param == "SS":
						type = "STRING"
						add_conv = conv_from_string_id % { "what" : chr(ord('a') + idx) }
					else:
						error("Unsupported print type '%s'" % param)
					code = add_conv + """
					{
						llvm::Function *print_func = get_runtime_func(RT_MDL_PRINT_%(type)s);
						ctx->CreateCall2(print_func, buf, %(param)s);
					}
					"""
				elif vector_chk:
					size = vector_chk[1]
					type = vector_chk[0].upper()
					code = """
					{
						llvm::Function *print_func  = get_runtime_func(RT_MDL_PRINT_%(type)s);
						llvm::Function *prints_func = get_runtime_func(RT_MDL_PRINT_STRING);
						llvm::Type     *arg_tp      = %(param)s->getType();

						llvm::Value *comma = ctx.get_constant("<");
						llvm::Value *next  = ctx.get_constant(", ");
						if (llvm::isa<llvm::ArrayType>(arg_tp)) {
							unsigned idxes[1];

							for (unsigned i = 0; i < %(size)d; ++i) {
								ctx->CreateCall2(prints_func, buf, comma);
								comma = next;
								idxes[0] = i;

								llvm::Value *elem = ctx->CreateExtractValue(%(param)s, idxes);
								ctx->CreateCall2(print_func, buf, elem);
							}
						} else {
							for (int i = 0; i < %(size)d; ++i) {
								ctx->CreateCall2(prints_func, buf, comma);
								comma = next;

								llvm::Value *idx  = ctx.get_constant(i);
								llvm::Value *elem = ctx->CreateExtractElement(%(param)s, idx);
								ctx->CreateCall2(print_func, buf, elem);
							}
						}
						llvm::Value *end = ctx.get_constant(">");
						ctx->CreateCall2(prints_func, buf, end);
					}
					"""
				else:
					error("Unsupported debug::print() parameter type '%s'" % param)
					code = """
					(void)%(param)s;
					"""
				self.format_code(f, code % { "type" : type, "size" : size, "param" : chr(ord('a') + idx) })
				idx = idx + 1
			# epilog
			code = """
					llvm::Function *end_func = get_runtime_func(RT_MDL_PRINT_END);
					ctx->CreateCall(end_func, buf);
				}
			"""
			self.format_code(f, code)
			self.format_code(f, "res = ctx.get_constant(true);\n")


		elif mode == "state::zero_return":
			# suppress unused variable warnings
			idx = 0
			for param in params:
				self.write(f, "(void)%s;\n" % chr(ord('a') + idx))
				idx += 1
			self.write(f, "res = llvm::Constant::getNullValue(ctx_data->get_return_type());\n")

		elif mode == "df::attr_lookup":
			# light profile or bsdf measurement attribute
			code_params = { "TYPE" : "LIGHT_PROFILE" }
			if intrinsic == "light_profile_power":
				code_params["name"] = "POWER"
			elif intrinsic == "light_profile_maximum":
				code_params["name"] = "MAXIMUM"
			elif intrinsic == "light_profile_isvalid":
				code_params["name"] = "VALID"
			elif intrinsic == "bsdf_measurement_isvalid":
				code_params["TYPE"] = "BSDF_MEASUREMENT"
				code_params["name"] = "VALID"
			code = """
			if (m_has_res_handler) {
				llvm::Function *glue_func = get_runtime_func(RT_MDL_DF_%(TYPE)s_%(name)s);
				res = ctx->CreateCall2(glue_func, res_data, a);
			} else {
				llvm::Type  *res_type = ctx_data->get_return_type();
				llvm::Value *lut      = m_code_gen.get_attribute_table(
					ctx, LLVM_code_generator::RTK_%(TYPE)s);
				llvm::Value *lut_size =  m_code_gen.get_attribute_table_size(
					ctx, LLVM_code_generator::RTK_%(TYPE)s);
				if (lut != NULL) {
					// have a lookup table
					llvm::Value *tmp  = ctx.create_local(res_type, "tmp");

					llvm::Value *cond = ctx->CreateICmpULT(a, lut_size);

					llvm::BasicBlock *lut_bb = ctx.create_bb("lut_bb");
					llvm::BasicBlock *bad_bb = ctx.create_bb("bad_bb");
					llvm::BasicBlock *end_bb = ctx.create_bb("end");

					// we do not expect out of bounds here
					ctx.CreateWeightedCondBr(cond, lut_bb, bad_bb, 1, 0);
					{
						ctx->SetInsertPoint(lut_bb);

						llvm::Value *select[] = {
							a,
							ctx.get_constant(int(Type_mapper::LAE_%(name)s))
						};

						llvm::Value *adr = ctx->CreateInBoundsGEP(lut, select);
						llvm::Value *v   = ctx->CreateLoad(adr);

						ctx->CreateStore(v, tmp);
						ctx->CreateBr(end_bb);
					}
					{
						ctx->SetInsertPoint(bad_bb);
						ctx->CreateStore(llvm::Constant::getNullValue(res_type), tmp);
						ctx->CreateBr(end_bb);
					}
					{
						ctx->SetInsertPoint(end_bb);
						res = ctx->CreateLoad(tmp);
					}
				} else {
					// no lookup table
					res = llvm::Constant::getNullValue(res_type);
				}
			}
			""" % code_params
			self.format_code(f, code)

		elif mode == None:
			error("Mode not set for intrinsic: %s %s" % (intrinsic, signature))

		else:
			warning("Unsupported mode '%s' for intrinsic: (%s %s)" % (mode, intrinsic, signature))

			# suppress unused variable warnings
			idx = 0
			for param in params:
				self.write(f, "(void)%s;\n" % chr(ord('a') + idx))
				idx += 1
			self.write(f, "res = llvm::UndefValue::get(ctx_data->get_return_type());\n")

		self.write(f, "ctx.create_return(res);\n")
		self.write(f, "return func;\n")

	def handle_signatures(self, f, intrinsic, signatures):
		"""Create code all sigtatures of one intrinsic."""
		if len(signatures) == 1:
			# no overloads
			params = signatures[0].split('_')[1:]
			if params == ['']:
				# fix for (void) signature
				params = []

			block = self.gen_condition(f, params, not self.strict)
			if block:
				self.indent += 1

			self.create_lazy_ir_construction(f, intrinsic, signatures[0])

			if block:
				self.indent -= 1
				self.write(f, "}\n")
		else:
			# have overloads
			signatures.sort()
			pre_if = ""
			for sig in signatures:
				params = sig.split('_')[1:]
				self.gen_condition(f, params, False, pre_if)
				pre_if = "} else "
				self.indent += 1
				self.create_lazy_ir_construction(f, intrinsic, sig)
				self.indent -= 1
			self.write(f, "}\n")

	def get_function_index(self, intrinsic_signature_pair):
		"""Get the index for a given intrinsic seiganture pair"""
		return self.m_func_index[intrinsic_signature_pair]

	def create_function_index(self, intrinsic_signature_pair):
		"""Get the index for a given intrinsic seiganture pair"""
		if self.m_func_index.get(intrinsic_signature_pair) != None:
			error("Signature pair '%s'already in use" % str(intrinsic_signature_pair))
		self.m_func_index[intrinsic_signature_pair] = self.m_next_func_index;
		self.m_next_func_index += 1;

	def handle_intrinsic(self, f, intrinsic):
		"""Create code for one intrinsic."""
		sigs = self.m_intrinsics[intrinsic]

		# order all signatures by ascending lenght
		l = {}
		for sig in sigs:
			sig_token = sig.split('_')
			n_params = len(sig_token) - 1
			if n_params == 1 and sig_token[1] == '':
				n_params = 0

			l.setdefault(n_params, []).append(sig)

		if len(l.keys()) == 1:
			# typical case: all signatures have the same length
			n_param = l.keys()[0]
			if self.strict:
				self.write(f, "if (n_params == %d) {\n" % n_param)
				self.indent += 1
			else:
				# create just an assertion
				self.write(f, "MDL_ASSERT(n_params == %d);\n" % n_param)

			for n_param in l.keys():
				self.handle_signatures(f, intrinsic, l[n_param])

			if self.strict:
				self.indent -= 1
				self.write(f, "}\n")
		else:
			# overloads with different signature length
			self.write(f, "switch (n_params) {\n")
			n_params = l.keys()
			n_params.sort()
			for n_param in n_params:
				self.write(f, "case %d:\n" % n_param)

				self.indent += 1
				self.write(f, "{\n")
				self.indent += 1
				self.handle_signatures(f, intrinsic, l[n_param])
				self.indent -= 1
				self.write(f, "}\n")

				self.write(f, "break;\n")
				self.indent -= 1

			self.write(f, "}\n")

	def create_type_sig_tuple(self, params):
		"""Create a type signature tuple (a, b) for a signature a_b."""
		res = []
		comma = ""
		for param in params:
			try:
				type_name = self.m_inv_types[param]
			except KeyError, e:
				error("Unknown type_code '%s' found" % param)
				sys.exit(1)
			res.append(type_name)
		return "(" + ", ".join(res) + ")"

	def gen_type_check(self, f, idx, type_code):
		"""Create a check for the idx parameter to be of given type."""
		atomic_chk = self.get_atomic_type_kind(type_code)

		self.write(f, "f_type->get_parameter(%s, p_type, p_sym);\n" % idx)
		self.write(f, "p_type = p_type->skip_type_alias();\n")
		if atomic_chk:
			self.write(f, "if (p_type->get_kind() != %s)\n" % (atomic_chk))
			self.indent += 1
			self.write(f, "return false;\n")
			self.indent -= 1
		elif type_code[0] == 'E':
			# check for enum type only, should be enough, we do not expect overloads with different
			# enum types
			self.write(f, "if (p_type->get_kind() != mi::mdl::IType::TK_ENUM)\n")
			self.indent += 1
			self.write(f, "return false;\n")
			self.indent -= 1
		else:
			vector_chk = self.get_vector_type_kind(type_code)
			matrix_chk = self.get_matrix_type_kind(type_code)
			text_shape = self.get_texture_shape(type_code)
			if vector_chk:
				self.write(f, "if (mi::mdl::IType_vector const *v_type = as<mi::mdl::IType_vector>(p_type)) {\n")
				self.indent += 1

				self.write(f, "if (v_type->get_size() != %s)\n" % type_code[-1])
				self.indent += 1
				self.write(f, "return false;\n")
				self.indent -= 1

				self.write(f, "mi::mdl::IType_atomic const *e_type = v_type->get_element_type();\n")
				self.write(f, "if (e_type->get_kind() != %s)\n" % vector_chk)
				self.indent += 1
				self.write(f, "return false;\n")
				self.indent -= 1

				self.indent -= 1

				self.write(f, "} else {\n")

				self.indent += 1
				self.write(f, "return false;\n")
				self.indent -= 1

				self.write(f, "}\n")
			elif matrix_chk:
				self.write(f, "if (mi::mdl::IType_matrix const *m_type = as<mi::mdl::IType_matrix>(p_type)) {\n")
				self.indent += 1

				self.write(f, "if (m_type->get_columns() != %s)\n" % type_code[-2])
				self.indent += 1
				self.write(f, "return false;\n")
				self.indent -= 1

				self.write(f, "mi::mdl::IType_vector const *v_type = m_type->get_element_type();\n")
				self.write(f, "if (v_type->get_size() != %s)\n" % type_code[-1])
				self.indent += 1
				self.write(f, "return false;\n")
				self.indent -= 1

				self.write(f, "mi::mdl::IType_atomic const *e_type = v_type->get_element_type();\n")
				self.write(f, "if (e_type->get_kind() != %s)\n" % matrix_chk)
				self.indent += 1
				self.write(f, "return false;\n")
				self.indent -= 1

				self.indent -= 1

				self.write(f, "} else {\n")

				self.indent += 1
				self.write(f, "return false;\n")
				self.indent -= 1

				self.write(f, "}\n")
			elif text_shape:
				self.write(f, "if (mi::mdl::IType_texture const *t_type = as<mi::mdl::IType_texture>(p_type)) {\n")
				self.indent += 1
				self.write(f, "if (t_type->get_shape() != %s)\n" % text_shape)
				self.indent += 1
				self.write(f, "return false;\n")
				self.indent -= 1
				self.indent -= 1
				self.write(f, "}\n")
			else:
				self.write(f, "// Unsupported\n");
				self.write(f, "return false;\n")

	def create_signature_checker(self, f):
		"""Create all signature checker functions."""
		signatures = self.m_signatures.keys()
		signatures.sort()
		for sig in signatures:
			if sig == '':
				# we don't need a check for the (void) signature
				continue

			params = sig.split('_')
			self.write(f, "/// Check that the given arguments have the signature %s.\n" % self.create_type_sig_tuple(params))
			self.write(f, "///\n")
			self.write(f, "/// \\param f_type  an MDL function type\n")
			self.write(f, "static bool check_sig_%s(mi::mdl::IType_function const *f_type)\n" % sig)
			self.write(f, "{\n")
			self.indent += 1

			self.write(f, "mi::mdl::IType const   *p_type;\n")
			self.write(f, "mi::mdl::ISymbol const *p_sym;\n")

			i = -1
			last_p = None
			seq = 0
			params.append(None) # add a sentinal
			for param in params:
				if last_p != param:
					if seq == 0:
						pass
					elif seq > 1:
						self.write(f, "for (size_t i = %d; i < %d; ++i) {\n" % (i - seq + 1, i + 1))
						self.indent += 1
						self.gen_type_check(f, 'i', last_p)
						self.indent -= 1
						self.write(f, "}\n")
					else:
						self.gen_type_check(f, str(i), last_p)
					last_p = param
					seq = 1
				else:
					seq += 1
				i += 1

			self.write(f, "return true;\n")

			self.indent -= 1
			self.write(f, "}\n\n")

	def write_access_specifier(self, f, specifier):
		"""Write a class access specifier"""
		self.indent -= 1
		self.write(f, "\n%s:\n" % specifier)
		self.indent += 1

	def add_class_member(self, type, name, comment = None, from_constructor = False):
		"""Add a class member to the generator class"""
		self.m_class_members[name] = (type, name, comment, from_constructor)
		self.m_class_member_names.append(name)

	def generate_class_members(self, f):
		"""Generate all class members of the generator class"""
		self.write_access_specifier(f, "private")

		for key in self.m_class_member_names:
			type, name, comment, _ = self.m_class_members[key]

			if comment:
				self.write(f, "// %s\n" % comment)
			space = ' '
			if type[-1] == '&' or type[-1] == '*':
				space = ''
			self.write(f, "%s%s%s;\n\n" % (type, space, name))

	def generate_constructor_comment(self, f):
		"""Generate the doxygen comments for the constructor."""
		self.write(f, "/// Constructor.\n")

		keys = self.m_class_member_names

		if len(keys) == 0:
			return
		self.write(f, "///\n")

		max_len = 0
		for key in keys:
			_, name, _, from_constr = self.m_class_members[key]
			if not from_constr:
				continue
			l = len(name)
			if l > max_len:
				max_len = l
		max_len += 1

		for key in keys:
			type, name, comment, from_constr = self.m_class_members[key]
			if not from_constr:
				continue

			space = ' ' * (max_len - len(name))
			if comment:
				self.write(f, "/// \param %s%s%s\n" % (name[2:], space, comment))
			else:
				self.write(f, "/// \param %s\n" % name[2:])

	def generate_constructor_parameter(self, f):
		"""Generate the parameter for the constructor."""
		keys = self.m_class_member_names

		if len(keys) == 0:
			f.write("()\n")
			return
		self.indent += 1

		max_len = 0
		for key in keys:
			type, _, _, from_constr = self.m_class_members[key]
			if not from_constr:
				continue

			l = len(type)
			if type[-1] != '*' and type[-1] != '&':
				l += 1
			if l > max_len:
				max_len = l

		comma = '('
		for key in keys:
			type, name, comment, from_constr = self.m_class_members[key]
			if not from_constr:
				continue

			space = ' ' * (max_len - len(type))
			f.write(comma + '\n')
			comma = ','
			if type[-1] == '&':
				# cannot pass references, because we are constructor through templates
				type = type[:-1] + '*'
			self.write(f, "%s%s%s" % (type, space, name[2:]))
		f.write(')\n')

		self.indent -= 1

		comma = ':'
		for key in keys:
			type, name, _, from_constr = self.m_class_members[key]
			if not from_constr:
				continue

			if type[-1] == '&':
				# passed by pointer, convert back to reference
				self.write(f, "%s %s(*%s)\n" % (comma, name, name[2:]))
			else:
				self.write(f, "%s %s(%s)\n" % (comma, name, name[2:]))
			comma = ','

	def create_constructor(self, f):
		"""Create the constructor for the class."""

		self.generate_constructor_comment(f)
		self.write(f, "MDL_runtime_creator")
		self.generate_constructor_parameter(f)

		code = """
		{
			m_use_user_state_module = false;
			for (size_t i = 0, n = dimension_of(m_runtime_funcs); i < n; ++i) {
				m_runtime_funcs[i] = NULL;
			}

			for (size_t i = 0, n = dimension_of(m_intrinsics); i < n; ++i) {
				m_intrinsics[i] = NULL;
			} 

			for (size_t i = 0, n = dimension_of(m_internal_funcs); i < n; ++i) {
				m_internal_funcs[i] = NULL;
			}
		}

		"""
		self.format_code(f, code)

	def register_c_runtime(self):
		"""Register functions from the C runtime."""

		# note: this sewction contains only functions supported in the C-runtime of Windows and Linux
		self.register_runtime_func("absi",   "II_II")
		self.register_runtime_func("absf",   "FF_FF")
		self.register_runtime_func("abs",    "DD_DD")
		self.register_runtime_func("acos",   "DD_DD")
		self.register_runtime_func("acosf",  "FF_FF")
		self.register_runtime_func("asin",   "DD_DD")
		self.register_runtime_func("asinf",  "FF_FF")
		self.register_runtime_func("atan",   "DD_DD")
		self.register_runtime_func("atanf",  "FF_FF")
		self.register_runtime_func("atan2",  "DD_DDDD")
		self.register_runtime_func("atan2f", "FF_FFFF")
		self.register_runtime_func("ceil",   "DD_DD")
		self.register_runtime_func("ceilf",  "FF_FF")
		self.register_runtime_func("cos",    "DD_DD")
		self.register_runtime_func("cosf",   "FF_FF")
		self.register_runtime_func("exp",    "DD_DD")
		self.register_runtime_func("expf",   "FF_FF")
		self.register_runtime_func("floor",  "DD_DD")
		self.register_runtime_func("floorf", "FF_FF")
		self.register_runtime_func("fmod",   "DD_DDDD")
		self.register_runtime_func("fmodf",  "FF_FFFF")
		self.register_runtime_func("log",    "DD_DD")
		self.register_runtime_func("logf",   "FF_FF")
		self.register_runtime_func("log10",  "DD_DD")
		self.register_runtime_func("log10f", "FF_FF")
		self.register_runtime_func("modf",   "DD_DDdd")
		self.register_runtime_func("modff",  "FF_FFff")
		self.register_runtime_func("pow",    "DD_DDDD")
		self.register_runtime_func("powf",   "FF_FFFF")
		self.register_runtime_func("powi",   "DD_DDII")
		self.register_runtime_func("sin",    "DD_DD")
		self.register_runtime_func("sinf",   "FF_FF")
		self.register_runtime_func("sqrt",   "DD_DD")
		self.register_runtime_func("sqrtf",  "FF_FF")
		self.register_runtime_func("tan",    "DD_DD")
		self.register_runtime_func("tanf",   "FF_FF")
		# extra used by other functions
		self.register_runtime_func("copysign",  "DD_DDDD")
		self.register_runtime_func("copysignf", "FF_FFFF")
		# optional supported
		self.register_runtime_func("sincosf", "VV_FFffff")
		self.register_runtime_func("exp2f",   "FF_FF")
		self.register_runtime_func("exp2",    "DD_DD")
		self.register_runtime_func("log2f",   "FF_FF")
		self.register_runtime_func("log2",    "DD_DD")
		self.register_runtime_func("mini",    "II_IIII")
		self.register_runtime_func("maxi",    "II_IIII")
		self.register_runtime_func("minf",    "FF_FFFF")
		self.register_runtime_func("maxf",    "FF_FFFF")
		self.register_runtime_func("min",     "DD_DDDD")
		self.register_runtime_func("max",     "DD_DDDD")
		self.register_runtime_func("rsqrtf",  "FF_FF")
		self.register_runtime_func("rsqrt",   "DD_DD")

	def register_atomic_runtime(self):
		self.register_mdl_runtime_func("mdl_clampi",      "II_IIIIII")
		self.register_mdl_runtime_func("mdl_clampf",      "FF_FFFFFF")
		self.register_mdl_runtime_func("mdl_clamp",       "DD_DDDDDD")
		self.register_mdl_runtime_func("mdl_exp2f",       "FF_FF")
		self.register_mdl_runtime_func("mdl_exp2",        "DD_DD")
		self.register_mdl_runtime_func("mdl_fracf",       "FF_FF")
		self.register_mdl_runtime_func("mdl_frac",        "DD_DD")
		self.register_mdl_runtime_func("mdl_log2f",       "FF_FF")
		self.register_mdl_runtime_func("mdl_log2",        "DD_DD")
		self.register_mdl_runtime_func("mdl_powi",        "II_IIII")
		self.register_mdl_runtime_func("mdl_roundf",      "FF_FF")
		self.register_mdl_runtime_func("mdl_round",       "DD_DD")
		self.register_mdl_runtime_func("mdl_rsqrtf",      "FF_FF")
		self.register_mdl_runtime_func("mdl_rsqrt",       "DD_DD")
		self.register_mdl_runtime_func("mdl_saturatef",   "FF_FF")
		self.register_mdl_runtime_func("mdl_saturate",    "DD_DD")
		self.register_mdl_runtime_func("mdl_signi",       "II_II")
		self.register_mdl_runtime_func("mdl_signf",       "FF_FF")
		self.register_mdl_runtime_func("mdl_sign",        "DD_DD")
		self.register_mdl_runtime_func("mdl_smoothstepf", "FF_FFFFFF")
		self.register_mdl_runtime_func("mdl_smoothstep",  "DD_DDDDDD")
		self.register_mdl_runtime_func("mdl_blackbody",   "FA3_FF")
		# extra used by other functions
		self.register_mdl_runtime_func("mdl_mini",        "II_IIII")
		self.register_mdl_runtime_func("mdl_minf",        "FF_FFFF")
		self.register_mdl_runtime_func("mdl_min",         "DD_DDDD")
		self.register_mdl_runtime_func("mdl_maxi",        "II_IIII")
		self.register_mdl_runtime_func("mdl_maxf",        "FF_FFFF")
		self.register_mdl_runtime_func("mdl_max",         "DD_DDDD")
		# tex functions
		self.register_mdl_runtime_func("mdl_tex_resolution_2d", "IA2_PTIIIA2")
		self.register_mdl_runtime_func("mdl_tex_width",         "II_PTII")
		self.register_mdl_runtime_func("mdl_tex_height",        "II_PTII")
		self.register_mdl_runtime_func("mdl_tex_depth",         "II_PTII")
		self.register_mdl_runtime_func("mdl_tex_valid",         "BB_PTII")

		self.register_mdl_runtime_func("mdl_tex_lookup_float_2d",    "FF_PTIIFA2EWMEWMFA2FA2")
		self.register_mdl_runtime_func("mdl_tex_lookup_float_3d",    "FF_PTIIFA3EWMEWMEWMFA2FA2FA2")
		self.register_mdl_runtime_func("mdl_tex_lookup_float_cube",  "FF_PTIIFA3")
		self.register_mdl_runtime_func("mdl_tex_lookup_float_ptex",  "FF_PTIIII")

		self.register_mdl_runtime_func("mdl_tex_lookup_float2_2d",   "FA2_PTIIFA2EWMEWMFA2FA2")
		self.register_mdl_runtime_func("mdl_tex_lookup_float2_3d",   "FA2_PTIIFA3EWMEWMEWMFA2FA2FA2")
		self.register_mdl_runtime_func("mdl_tex_lookup_float2_cube", "FA2_PTIIFA3")
		self.register_mdl_runtime_func("mdl_tex_lookup_float2_ptex", "FA2_PTIIII")

		self.register_mdl_runtime_func("mdl_tex_lookup_float3_2d",   "FA3_PTIIFA2EWMEWMFA2FA2")
		self.register_mdl_runtime_func("mdl_tex_lookup_float3_3d",   "FA3_PTIIFA3EWMEWMEWMFA2FA2FA2")
		self.register_mdl_runtime_func("mdl_tex_lookup_float3_cube", "FA3_PTIIFA3")
		self.register_mdl_runtime_func("mdl_tex_lookup_float3_ptex", "FA3_PTIIII")

		self.register_mdl_runtime_func("mdl_tex_lookup_float4_2d",   "FA4_PTIIFA2EWMEWMFA2FA2")
		self.register_mdl_runtime_func("mdl_tex_lookup_float4_3d",   "FA4_PTIIFA3EWMEWMEWMFA2FA2FA2")
		self.register_mdl_runtime_func("mdl_tex_lookup_float4_cube", "FA4_PTIIFA3")
		self.register_mdl_runtime_func("mdl_tex_lookup_float4_ptex", "FA4_PTIIII")

		self.register_mdl_runtime_func("mdl_tex_lookup_color_2d",    "FA3_PTIIFA2EWMEWMFA2FA2")
		self.register_mdl_runtime_func("mdl_tex_lookup_color_3d",    "FA3_PTIIFA3EWMEWMEWMFA2FA2FA2")
		self.register_mdl_runtime_func("mdl_tex_lookup_color_cube",  "FA3_PTIIFA3")
		self.register_mdl_runtime_func("mdl_tex_lookup_color_ptex",  "FA3_PTIIII")

		self.register_mdl_runtime_func("mdl_tex_texel_float_2d",        "FF_PTIIIA2IA2")
		self.register_mdl_runtime_func("mdl_tex_texel_float2_2d",       "FA2_PTIIIA2IA2")
		self.register_mdl_runtime_func("mdl_tex_texel_float3_2d",       "FA3_PTIIIA2IA2")
		self.register_mdl_runtime_func("mdl_tex_texel_float4_2d",       "FA4_PTIIIA2IA2")
		self.register_mdl_runtime_func("mdl_tex_texel_color_2d",        "FA3_PTIIIA2IA2")

		self.register_mdl_runtime_func("mdl_tex_texel_float_3d",        "FF_PTIIIA3")
		self.register_mdl_runtime_func("mdl_tex_texel_float2_3d",       "FA2_PTIIIA3")
		self.register_mdl_runtime_func("mdl_tex_texel_float3_3d",       "FA3_PTIIIA3")
		self.register_mdl_runtime_func("mdl_tex_texel_float4_3d",       "FA4_PTIIIA3")
		self.register_mdl_runtime_func("mdl_tex_texel_color_3d",        "FA3_PTIIIA3")

		# df functions
		self.register_mdl_runtime_func("mdl_df_light_profile_power",    "FF_PTII")
		self.register_mdl_runtime_func("mdl_df_light_profile_maximum",  "FF_PTII")
		self.register_mdl_runtime_func("mdl_df_light_profile_valid",    "BB_PTII")
		self.register_mdl_runtime_func("mdl_df_bsdf_measurement_valid", "BB_PTII")

		# exception handling
		self.register_mdl_runtime_func("mdl_out_of_bounds",          "VV_xsIIZZCSII")
		self.register_mdl_runtime_func("mdl_div_by_zero",            "VV_xsCSII")

		# debug support
		self.register_mdl_runtime_func("mdl_debugbreak",             "VV_")
		self.register_mdl_runtime_func("mdl_assertfail",             "VV_CSCSCSII")
		self.register_mdl_runtime_func("__assertfail",               "VV_CSCSIICSZZ")
		self.register_mdl_runtime_func("mdl_print_begin",            "lb_")
		self.register_mdl_runtime_func("mdl_print_end",              "VV_lb")
		self.register_mdl_runtime_func("mdl_print_bool",             "VV_lbBB")
		self.register_mdl_runtime_func("mdl_print_int",              "VV_lbII")
		self.register_mdl_runtime_func("mdl_print_float",            "VV_lbFF")
		self.register_mdl_runtime_func("mdl_print_double",           "VV_lbDD")
		self.register_mdl_runtime_func("mdl_print_string",           "VV_lbCS")
		self.register_mdl_runtime_func("vprintf",                    "II_CSvv")

		# string ID support
		self.register_mdl_runtime_func("mdl_to_cstring",             "CS_SS")

		# JIT support
		self.register_mdl_runtime_func("mdl_tex_res_float",          "FF_scII")
		self.register_mdl_runtime_func("mdl_tex_res_float3",         "F3_scII")
		self.register_mdl_runtime_func("mdl_tex_res_color",          "CC_scII")

	def generate_runtime_enum(self, f):
		"""Generate the enum for the runtime functions."""
		self.write(f, "/// Used functions from the C-runtime.\n")
		self.write(f, "enum Runtime_function {\n")
		self.indent += 1
		last = None
		self.write(f, "RT_C_FIRST,\n")
		init = " = RT_C_FIRST"
		keys = self.m_c_runtime_functions.keys()
		keys.sort()
		for func in keys:
			enum_value = "RT_" + func
			enum_value = enum_value.upper()
			last = enum_value
			self.write(f, "%s%s,\n" % (enum_value.upper(), init))
			init = ""
		self.write(f, "RT_C_LAST = %s,\n" % last.upper())

		self.write(f, "RT_MDL_FIRST,\n")
		init = " = RT_MDL_FIRST"
		keys = self.m_mdl_runtime_functions.keys()
		keys.sort()
		for func in keys:
			enum_value = "RT_" + func
			enum_value = enum_value.upper()
			last = enum_value
			self.write(f, "%s%s,\n" % (enum_value.upper(), init))
			init = ""
		self.write(f, "RT_MDL_LAST = %s,\n" % last.upper())

		self.write(f, "RT_LAST = RT_MDL_LAST\n")
		self.indent -= 1
		self.write(f, "};\n")

	def generate_runtime_func_cache(self, f):
		"""Generate the lazy runtime function getter."""
		self.write(f, "/// Get a runtime function lazily.\n")
		self.write(f, "///\n")
		self.write(f, "/// \\param code  The runtime function code.\n")
		self.write(f, "llvm::Function *get_runtime_func(Runtime_function code) {\n")
		self.indent += 1
		self.write(f, "llvm::Function *func = m_runtime_funcs[code];\n")

		self.write(f, "if (func != NULL)\n")
		self.indent += 1
		self.write(f, "return func;\n")
		self.indent -= 1

		self.write(f, "switch (code) {\n")

		for name, signature in self.m_c_runtime_functions.iteritems():
			enum_value = "RT_" + name
			enum_value = enum_value.upper()
			self.write(f, "case %s:\n" % enum_value)
			self.indent += 1
			self.write(f, 'func = get_c_runtime_func(%s, "%s");\n' % (enum_value, signature))
			self.write(f, "break;\n")
			self.indent -= 1

		for name, signature in self.m_mdl_runtime_functions.iteritems():
			enum_value = "RT_" + name
			enum_value = enum_value.upper()
			self.write(f, "case %s:\n" % enum_value)
			self.indent += 1
			self.write(f, 'func = create_runtime_func(code, "%s", "%s");\n' % (name, signature))
			self.write(f, "break;\n")
			self.indent -= 1

		code ="""
		default:
			MDL_ASSERT(!"unsupported runtime function!");
			break;
		}
		m_runtime_funcs[code] = func;
		return func;
		"""
		self.format_code(f, code)

		self.indent -= 1
		self.write(f, "}\n")

		code = """
		/// Return an LLVM type for a (single type) signature.
		///
		/// \\param sig        The signature, will be moved.
		/// \\param by_ref     True if this type must passed by reference.
		llvm::Type *type_from_signature(
			char const * &sig,
			bool         &by_ref);

		/// Create a function declaration from a signature.
		///
		/// \\param[in]  name       The name of the C runtime function.
		/// \\param[in]  signature  The signature of the C runtime function.
		/// \\param[out] is_sret    Set to true, if this is a sret function, else set to false.
		llvm::Function *decl_from_signature(
			char const *name,
			char const *signature,
			bool       &is_sret);

		/// Get an external C-runtime function.
		///
		/// \\param func       The code of the C runtime function.
		/// \\param signature  The signature of the C runtime function.
		llvm::Function *get_c_runtime_func(
			Runtime_function func,
			char const *signature);

		/// Check if a given MDL runtime function exists inside the C-runtime.
		///
		/// \\param code       The (MDL) runtime function code.
		/// \\param signature  The signature of the runtime function.
		llvm::Function *find_in_c_runtime(
			Runtime_function code,
			char const       *signature);

		/// Create a runtime function.
		///
		/// \\param code       The runtime function code.
		/// \\param name       The name of the runtime function.
		/// \\param signature  The signature of the runtime function.
		llvm::Function *create_runtime_func(
			Runtime_function code,
			char const *name,
			char const *signature);

		/// Load an runtime function arguments value.
		///
		/// \param ctx  the current function context
		/// \param arg  the passed argument, either a reference or the value instead
		llvm::Value *load_by_value(Function_context &ctx, llvm::Value *arg);


		/// Get the start offset of the next entry with the given type in a valist.
		///
		/// \param offset        the offset into a valist in bytes pointing to after the last
		///                      entry. it will be advanced to after the new entry.
		/// \param operand_type  the operand type for the next entry
		int get_next_valist_entry_offset(int &offset, llvm::Type *operand_type);

		/// Get a pointer to the next entry in the given valist buffer.
		///
		/// \param ctx           the current function context
		/// \param valist        the valist buffer
		/// \param offset        the offset into valist in bytes pointing to after the last entry.
		///                      it will be advanced to after the new entry.
		/// \param operand_type  the operand type for the next entry
		llvm::Value *get_next_valist_pointer(Function_context &ctx,
			llvm::Value *valist, int &offset, llvm::Type *operand_type);

		/// Call a runtime function.
		///
		/// \param ctx     the current function context
		/// \param callee  the called function
		/// \param args    function arguments
		llvm::Value *call_rt_func(
			Function_context              &ctx,
			llvm::Function                *callee,
			llvm::ArrayRef<llvm::Value *> args);

		/// Call a void runtime function.
		///
		/// \param ctx     the current function context
		/// \param callee  the called function
		/// \param args    function arguments
		void call_rt_func_void(
			Function_context              &ctx,
			llvm::Function                *callee,
			llvm::ArrayRef<llvm::Value *> args);
		"""
		self.format_code(f, code)

	def create_intrinsic_func_indexes(self, intrinsics):
		"""Create function indexes for all intrinsic functions."""
		for intrinsic in intrinsics:
			sigs = self.m_intrinsics[intrinsic]

			# order all signatures by ascending lenght
			l = {}
			for sig in sigs:
				sig_token = sig.split('_')
				n_params = len(sig_token) - 1

				l.setdefault(n_params, []).append(sig)

			n_params = l.keys()
			n_params.sort()
			for n_param in n_params:
				signatures = l[n_param]
				signatures.sort()
				for sig in signatures:
					self.create_function_index((intrinsic, sig))

	def create_check_state_module(self, f):
		code = """
		/// Check whether the given module contains the given function and create an error if not.
		///
		/// \param mod        The module
		/// \param func_name  The function name
		/// \param ret_type   The return type the function should have, or NULL for not checking it
		/// \param optional   If true, no error will be generated when then function does not exist
		///
		/// \\returns true, if the module contains the function.
		bool check_function_exists(
				llvm::Module *mod,
				char const *func_name,
				llvm::Type *ret_type,
				bool optional)
		{
			llvm::Function *func = mod->getFunction(func_name);
			if (func == NULL) {
				if (optional) return true;
				m_code_gen.error(STATE_MODULE_FUNCTION_MISSING, func_name);
				return false;
			}

			if (ret_type != NULL && func->getReturnType() != ret_type) {
				m_code_gen.error(WRONG_RETURN_TYPE_FOR_STATE_MODULE_FUNCTION, func_name);
				return false;
			}
			return true;
		}

		/// Check whether the given module contains the given function returning a pointer
		/// and create an error if not.
		///
		/// \param mod        The module
		/// \param func_name  The function name
		///
		/// \\returns true, if the module contains the function.
		bool check_function_returns_pointer(llvm::Module *mod, char const *func_name) {
			llvm::Function *func = mod->getFunction(func_name);
			if (func == NULL) {
				m_code_gen.error(STATE_MODULE_FUNCTION_MISSING, func_name);
				return false;
			}

			if (!func->getReturnType()->isPointerTy()) {
				m_code_gen.error(WRONG_RETURN_TYPE_FOR_STATE_MODULE_FUNCTION, func_name);
				return false;
			}
			return true;
		}
		"""
		self.format_code(f, code)

		code = """
		/// Check whether the given module can be used as user-implemented state module.
		///
		/// \param mod     The module containing the user implementation of state.
		///
		/// \\returns true, if the module can be used as a user implementation of state.
		bool check_state_module(llvm::Module *mod) {
			bool success = true;

			#define HAS_FUNC(x, ret_type) if (!check_function_exists(mod, x, ret_type, false)) success = false;
			#define HAS_OPT_FUNC(x, ret_type) if (!check_function_exists(mod, x, ret_type, true)) success = false;

			llvm::Type *char_ptr_type = m_code_gen.m_type_mapper.get_char_ptr_type();
			llvm::Type *float_type = m_code_gen.m_type_mapper.get_float_type();
			llvm::Type *float_ptr_type = m_code_gen.m_type_mapper.get_float_ptr_type();
			llvm::Type *float3_type = m_code_gen.m_type_mapper.get_float3_type();
			llvm::Type *float3x3_type = m_code_gen.m_type_mapper.get_float3x3_type();
			llvm::Type *float4x4_type = m_code_gen.m_type_mapper.get_float4x4_type();
			llvm::Type *int_type = m_code_gen.m_type_mapper.get_int_type();
			llvm::Type *void_type = m_code_gen.m_type_mapper.get_void_type();

		"""
		self.format_code(f, code)

		# all these functions have to be defined with a State_core parameter
		state_core_intrinsics = [
			("position", "float3_type"),
			("normal", "float3_type"),
			("set_normal", "void_type"),
			("geometry_normal", "float3_type"),
			("motion", "float3_type"),
			("texture_coordinate", "float3_type"),
			("texture_tangent_u", "float3_type"),
			("texture_tangent_v", "float3_type"),
			("tangent_space", "float3x3_type"),
			("geometry_tangent_u", "float3_type"),
			("geometry_tangent_v", "float3_type"),
			("animation_time", "float_type"),
			("wavelength_base", "float_ptr_type"),
			("transform", "float4x4_type"),
			("transform_point", "float3_type"),
			("transform_normal", "float3_type"),
			("transform_vector", "float3_type"),
			("transform_scale", "float_type"),
			("object_id", "int_type"),
			("get_texture_results", "NULL"),
			("get_ro_data_segment", "char_ptr_type")
		]

		# optional functions with State_core parameter
		state_core_intrinsics_opt = [
			("rounded_corner_normal", "float3_type")
		]

		# all these functions have to be defined with a State_environment parameter
		state_env_intrinsics = [
			("direction", "float3_type")
		]

		for intrinsic, ret_type in state_core_intrinsics:
			self.write(f, "HAS_FUNC(\"%s\", %s)\n" % (
				self.get_mangled_state_func_name(intrinsic, "State_core"), ret_type))

		for intrinsic, ret_type in state_core_intrinsics_opt:
			self.write(f, "HAS_OPT_FUNC(\"%s\", %s)\n" % (
				self.get_mangled_state_func_name(intrinsic, "State_core"), ret_type))

		for intrinsic, ret_type in state_env_intrinsics:
			self.write(f, "HAS_FUNC(\"%s\", %s)\n" % (
				self.get_mangled_state_func_name(intrinsic, "State_environment"), ret_type))

		self.write(f, "\n")
		self.write(f, "if (!success) return false;\n")
		self.write(f, "m_use_user_state_module = true;\n")
		self.write(f, "return true;\n")
		self.indent -= 1
		self.write(f, "}\n")
		self.write(f, "\n")


	def finalize(self):
		"""Create output."""

		intrinsics = []
		unsupported = []
		for intrinsic in self.m_intrinsics.keys():
			if self.unsupported_intrinsics.get(intrinsic):
				# filter out unnsupported ones
				unsupported.append(intrinsic)
			else:
				intrinsics.append(intrinsic)
		unsupported.sort()
		intrinsics.sort()

		self.create_intrinsic_func_indexes(intrinsics)

		self.register_c_runtime()
		self.register_atomic_runtime();

		f = open(self.out_name, "w")

		# add class members
		self.add_class_member("mi::mdl::IAllocator *", "m_alloc",                      "The allocator.",               True)
		self.add_class_member("LLVM_code_generator &", "m_code_gen",                   "The code generator.",          True)
		self.add_class_member("bool",                  "m_ptx_mode",                   "True if destination is PTX.",  True)
		self.add_class_member("bool",                  "m_fast_math",                  "True if fast-math is enabled.",  True)
		self.add_class_member("bool",                  "m_has_sincosf",                "True if destination has sincosf.",  True)
		self.add_class_member("bool",                  "m_has_res_handler",            "True if a resource handler I/F is available.", True)
		self.add_class_member("bool",                  "m_use_user_state_module",      "True if user-defined state module functions should be used.", False)
		self.add_class_member("int",                   "m_internal_space",             "The internal_space encoding.", True)
		self.add_class_member("llvm::Function *",      "m_runtime_funcs[RT_LAST + 1]", "Runtime functions.",           False)
		self.add_class_member("llvm::Function *",      "m_intrinsics[%d]" % self.m_next_func_index, "Cache for intrinsic functions.", False)
		self.add_class_member("llvm::Function *",      "m_internal_funcs[Internal_function::KI_NUM_INTERNAL_FUNCTIONS]", "Cache for internal functions.", False)

		# start class
		self.write(f, "class MDL_runtime_creator {\n")
		self.indent += 1

		self.write_access_specifier(f, "public")
		self.write(f, "/// Number of supported intrinsics.\n")
		self.write(f, "static size_t const NUM_INTRINSICS = %d;\n\n" % self.m_next_func_index)
		self.generate_runtime_enum(f)

		self.write_access_specifier(f, "public")

		# generate the constructor
		self.create_constructor(f)

		# write prototypes of internal function creation functions
		self.write(f, "/// Generate LLVM IR for state::set_normal(float3)\n")
		self.write(f, "llvm::Function *create_state_set_normal(Internal_function const *int_func);\n\n")
		self.write(f, "/// Generate LLVM IR for state::get_texture_results()\n")
		self.write(f, "llvm::Function *create_state_get_texture_results(Internal_function const *int_func);\n\n")
		self.write(f, "/// Generate LLVM IR for state::get_ro_data_segment()\n")
		self.write(f, "llvm::Function *create_state_get_ro_data_segment(Internal_function const *int_func);\n\n")
		self.write(f, "/// Generate LLVM IR for state::object_id()\n")
		self.write(f, "llvm::Function *create_state_object_id(Internal_function const *int_func);\n")
		self.write(f, "\n")

		# generate the public functions
		self.write(f, "/// Generate LLVM IR for an internal function.\n")
		self.write(f, "///\n")
		self.write(f, "/// \\param int_func  Information about the internal function\n")
		self.write(f, "///\n")
		self.write(f, "/// \\return The LLVM Function object or NULL if the function could\n")
		self.write(f, "///         not be generated\n")
		self.write(f, "llvm::Function *get_internal_function(\n")
		self.indent += 1
		self.write(f, "Internal_function const *int_func);\n")
		self.indent -= 1
		self.write(f, "\n")

		self.create_check_state_module(f)

		self.write(f, "/// Generate LLVM IR for an intrinsic function.\n")
		self.write(f, "///\n")
		self.write(f, "/// \\param func_def  The definition of the intrinsic function\n")
		self.write(f, "///\n")
		self.write(f, "/// \\return The LLVM Function object or NULL if the function could\n")
		self.write(f, "///         not be generated\n")
		self.write(f, "llvm::Function *get_intrinsic_function(\n")
		self.indent += 1
		self.write(f, "mi::mdl::IDefinition const *func_def)\n")
		self.indent -= 1
		self.write(f, "{\n")

		self.indent += 1

		self.write(f, "mi::mdl::IType_function const *f_type  = cast<mi::mdl::IType_function>(func_def->get_type());\n")
		self.write(f, "int                           n_params = f_type->get_parameter_count();\n")
		self.write(f, "\n")

		self.write(f, "switch (func_def->get_semantics()) {\n")

		for intrinsic in intrinsics:
			mod_name = self.m_intrinsic_mods[intrinsic]
			self.write(f, "case mi::mdl::IDefinition::DS_INTRINSIC_%s_%s:\n" % (mod_name.upper(), intrinsic.upper()))
			self.indent += 1

			self.handle_intrinsic(f, intrinsic)
			self.write(f, "break;\n");

			self.indent -= 1

		for intrinsic in unsupported:
			mod_name = self.m_intrinsic_mods[intrinsic]
			self.write(f, "case mi::mdl::IDefinition::DS_INTRINSIC_%s_%s:\n" % (mod_name.upper(), intrinsic.upper()))

		if len(unsupported) > 0:
			self.indent += 1

			self.write(f, 'MDL_ASSERT(!"Cannot generate unsupported intrinsic");\n')
			self.write(f, "break;\n");

			self.indent -= 1


		self.write(f, "default:\n")
		self.indent += 1
		self.write(f, "break;\n");
		self.indent -= 1

		self.write(f, "}\n")
		self.write(f, "// cannot generate\n")
		self.write(f, "return NULL;\n")

		self.indent -= 1

		self.write(f, "}\n")

		self.generate_runtime_func_cache(f)

		# generate private helper functions
		self.write_access_specifier(f, "private")

		self.create_signature_checker(f)

		# create the constructor functions
		for intrinsic in intrinsics:
			sigs = self.m_intrinsics[intrinsic]

			# order all signatures by ascending lenght
			l = {}
			for sig in sigs:
				sig_token = sig.split('_')
				n_params = len(sig_token) - 1

				l.setdefault(n_params, []).append(sig)

			n_params = l.keys()
			n_params.sort()
			for n_param in n_params:
				sigs_same_len = l[n_param]
				for signature in sigs_same_len:
					self.create_ir_constructor(f, intrinsic, signature)

		self.generate_class_members(f)

		# end of the class
		self.indent -= 1
		self.write(f, "};\n")

		f.close()

def usage(args):
	"""print usage info and exit"""
	print "Usage: %s stdlib_directory outputfile" % args[0]
	return 1

def main(args):
	"""Process one file and generate signatures."""
	if len(args) != 3:
		return usage(args)

	stdlib_dir = args[1]
	out_name   = args[2]
	strict     = True

	try:
		parser = SignatureParser(args[0], stdlib_dir, out_name, strict)
		parser.parse("math")
		parser.parse("state")
		parser.parse("df")
		parser.parse("tex")
		parser.parse("debug")
		parser.finalize()

	except IOError, e:
		error(str(e))
		return 1
	return 0

if __name__ == "__main__":
	if len(sys.argv) == 1:
		# called 'as script': assume 64bit debug
		obj = os.environ['MI_OBJ'] + '/neuray_vc11/x64_Debug/mdl_jit_generator_jit';
		dbg_args = ["../../compiler/stdmodule",  obj + '/generator_jit_intrinsic_func.i']
		sys.exit(main([sys.argv[0]] + dbg_args))
	else:
		sys.exit(main(sys.argv))


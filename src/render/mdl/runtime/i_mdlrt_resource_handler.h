/***************************************************************************************************
 * Copyright (c) 2013-2018, NVIDIA CORPORATION. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *  * Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *  * Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *  * Neither the name of NVIDIA CORPORATION nor the names of its
 *    contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
 * OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 **************************************************************************************************/
///
/// \file
/// \brief Functionality to handle textures in jitted code
///

#ifndef RENDER_MDL_RUNTIME_I_MDLRT_RESOURCE_HANDLER_H
#define RENDER_MDL_RUNTIME_I_MDLRT_RESOURCE_HANDLER_H

#include <mi/mdl/mdl_generated_executable.h>
#include <mi/base/handle.h>

#include <base/system/main/neuray_cc_conf.h>

namespace MI {
namespace MDLRT {

/** \brief Resource handler helper.

 See \c mi::mdl::IResource_handler.
 */
class Resource_handler : public mi::mdl::IResource_handler {
public:
    /// Get the number of bytes that must be allocated for a resource object.
    virtual size_t get_data_size() const;

    /// Initializes a texture data helper object.
    ///
    /// \param data    an 16byte aligned pointer to allocated data of at least
    ///                get_data_size() bytes
    /// \param shape   the texture type shape to initialize
    /// \param tag     the texture tag
    /// \param gamma   the MDL declared gamma value of the texture
    /// \param ctx     a used defined context parameter
    void tex_init(
        void                                *data,
        mi::mdl::IType_texture::Shape       shape,
        unsigned                            tag,
        mi::mdl::IValue_texture::gamma_mode gamma,
        void                               *ctx) NEURAY_OVERRIDE;

    /// Terminate a texture data helper object.
    ///
    /// \param data   an 16byte aligned pointer to allocated data of at least
    ///               get_data_size() bytes
    /// \param shape  the texture type shape of the object to terminate
    void tex_term(
        void                          *data,
        mi::mdl::IType_texture::Shape shape) NEURAY_OVERRIDE;

    /// Handle tex::width(texture_2d, int2) and tex::height(texture_2d, int2)
    void tex_resolution_2d(
        int           result[2],
        void const    *tex_data,
        int const     uv_tile[2]) const NEURAY_OVERRIDE;

    /// Handle tex::width(texture_*) (not for udim textures)
    int tex_width(
        void const    *tex_data) const NEURAY_OVERRIDE;

    /// Handle tex::height(texture_*) (not for udim textures)
    int tex_height(
        void const    *tex_data) const NEURAY_OVERRIDE;

    /// Handle tex::depth(texture_*)
    int tex_depth(
        void const    *tex_data) const NEURAY_OVERRIDE;

    /// Handle tex::lookup_float(texture_2d, ...)
    float tex_lookup_float_2d(
        void const    *tex_data,
        void          *thread_data,
        float const   coord[2],
        Tex_wrap_mode wrap_u,
        Tex_wrap_mode wrap_v,
        float const   crop_u[2],
        float const   crop_v[2]) const NEURAY_OVERRIDE;

    /// Handle tex::lookup_float(texture_3d, ...)
    float tex_lookup_float_3d(
        void const    *tex_data,
        void          *thread_data,
        float const   coord[3],
        Tex_wrap_mode wrap_u,
        Tex_wrap_mode wrap_v,
        Tex_wrap_mode wrap_w,
        float const   crop_u[2],
        float const   crop_v[2],
        float const   crop_w[2]) const NEURAY_OVERRIDE;

    /// Handle tex::lookup_float(texture_cube, ...)
    float tex_lookup_float_cube(
        void const    *tex_data,
        void          *thread_data,
        float const   coord[3]) const NEURAY_OVERRIDE;

    /// Handle tex::lookup_float(texture_ptex, ...)
    float tex_lookup_float_ptex(
        void const    *tex_data,
        void          *thread_data,
        int           channel) const NEURAY_OVERRIDE;

    /// Handle tex::lookup_float2(texture_2d, ...)
    void tex_lookup_float2_2d(
        float         result[2],
        void const    *tex_data,
        void          *thread_data,
        float const   coord[2],
        Tex_wrap_mode wrap_u,
        Tex_wrap_mode wrap_v,
        float const   crop_u[2],
        float const   crop_v[2]) const NEURAY_OVERRIDE;

    /// Handle tex::lookup_float2(texture_3d, ...)
    void tex_lookup_float2_3d(
        float         result[2],
        void const    *tex_data,
        void          *thread_data,
        float const   coord[3],
        Tex_wrap_mode wrap_u,
        Tex_wrap_mode wrap_v,
        Tex_wrap_mode wrap_w,
        float const   crop_u[2],
        float const   crop_v[2],
        float const   crop_w[2]) const NEURAY_OVERRIDE;

    /// Handle tex::lookup_float2(texture_cube, ...)
    void tex_lookup_float2_cube(
        float         result[2],
        void const    *tex_data,
        void          *thread_data,
        float const   coord[3]) const NEURAY_OVERRIDE;

    // Handle tex::lookup_float2(texture_ptex, ...)
    void tex_lookup_float2_ptex(
        float         result[2],
        void const    *tex_data,
        void          *thread_data,
        int           channel) const NEURAY_OVERRIDE;

    /// Handle tex::lookup_float3(texture_2d, ...)
    void tex_lookup_float3_2d(
        float         result[3],
        void const    *tex_data,
        void          *thread_data,
        float const   coord[2],
        Tex_wrap_mode wrap_u,
        Tex_wrap_mode wrap_v,
        float const   crop_u[2],
        float const   crop_v[2]) const NEURAY_OVERRIDE;

    /// Handle tex::lookup_float3(texture_3d, ...)
    void tex_lookup_float3_3d(
        float         result[3],
        void const    *tex_data,
        void          *thread_data,
        float const   coord[3],
        Tex_wrap_mode wrap_u,
        Tex_wrap_mode wrap_v,
        Tex_wrap_mode wrap_w,
        float const   crop_u[2],
        float const   crop_v[2],
        float const   crop_w[2]) const NEURAY_OVERRIDE;

    /// Handle tex::lookup_float3(texture_cube, ...)
    void tex_lookup_float3_cube(
        float         result[3],
        void const    *tex_data,
        void          *thread_data,
        float const   coord[3]) const NEURAY_OVERRIDE;

    /// Handle tex::lookup_float3(texture_ptex, ...)
    void tex_lookup_float3_ptex(
        float         result[3],
        void const    *tex_data,
        void          *thread_data,
        int           channel) const NEURAY_OVERRIDE;

    /// Handle tex::lookup_float4(texture_2d, ...)
    void tex_lookup_float4_2d(
        float         result[4],
        void const    *tex_data,
        void          *thread_data,
        float const   coord[2],
        Tex_wrap_mode wrap_u,
        Tex_wrap_mode wrap_v,
        float const   crop_u[2],
        float const   crop_v[2]) const NEURAY_OVERRIDE;

    /// Handle tex::lookup_float4(texture_3d, ...)
    void tex_lookup_float4_3d(
        float         result[4],
        void const    *tex_data,
        void          *thread_data,
        float const   coord[3],
        Tex_wrap_mode wrap_u,
        Tex_wrap_mode wrap_v,
        Tex_wrap_mode wrap_w,
        float const   crop_u[2],
        float const   crop_v[2],
        float const   crop_w[2]) const NEURAY_OVERRIDE;

    /// Handle tex::lookup_float4(texture_cube, ...)
    void tex_lookup_float4_cube(
        float         result[4],
        void const    *tex_data,
        void          *thread_data,
        float const   coord[3]) const NEURAY_OVERRIDE;

    /// Handle tex::lookup_float4(texture_ptex, ...)
    void tex_lookup_float4_ptex(
        float         result[4],
        void const    *tex_data,
        void          *thread_data,
        int           channel) const NEURAY_OVERRIDE;

    /// Handle tex::lookup_color(texture_2d, ...)
    void tex_lookup_color_2d(
        float         rgb[3],
        void const    *tex_data,
        void          *thread_data,
        float const   coord[2],
        Tex_wrap_mode wrap_u,
        Tex_wrap_mode wrap_v,
        float const   crop_u[2],
        float const   crop_v[2]) const NEURAY_OVERRIDE;

    /// Handle tex::lookup_color(texture_2d, ...)
    void tex_lookup_color_3d(
        float         rgb[3],
        void const    *tex_data,
        void          *thread_data,
        float const   coord[3],
        Tex_wrap_mode wrap_u,
        Tex_wrap_mode wrap_v,
        Tex_wrap_mode wrap_w,
        float const   crop_u[2],
        float const   crop_v[2],
        float const   crop_w[2]) const NEURAY_OVERRIDE;

    /// Handle tex::lookup_color(texture_cube, ...)
    void tex_lookup_color_cube(
        float         rgb[3],
        void const    *tex_data,
        void          *thread_data,
        float const   coord[3]) const NEURAY_OVERRIDE;

    /// Handle tex::lookup_color(texture_ptex, ...)
    void tex_lookup_color_ptex(
        float         rgb[3],
        void const    *tex_data,
        void          *thread_data,
        int           channel) const NEURAY_OVERRIDE;

    /// Handle tex::texel_float(texture_2d, ...)
    float tex_texel_float_2d(
        void const    *tex_data,
        void          *thread_data,
        int const     coord[2],
        int const     uv_tile[2]) const NEURAY_OVERRIDE;

    /// Handle tex::texel_float2(texture_2d, ...)
    void tex_texel_float2_2d(
        float         result[2],
        void const    *tex_data,
        void          *thread_data,
        int const     coord[2],
        int const     uv_tile[2]) const NEURAY_OVERRIDE;

    /// Handle tex::texel_float3(texture_2d, ...)
    void tex_texel_float3_2d(
        float         result[3],
        void const    *tex_data,
        void          *thread_data,
        int const     coord[2],
        int const     uv_tile[2]) const NEURAY_OVERRIDE;

    /// Handle tex::texel_float4(texture_2d, ...)
    void tex_texel_float4_2d(
        float         result[4],
        void const    *tex_data,
        void          *thread_data,
        int const     coord[2],
        int const     uv_tile[2]) const NEURAY_OVERRIDE;

    /// Handle tex::texel_color(texture_2d, ...)
    void tex_texel_color_2d(
        float         rgb[3],
        void const    *tex_data,
        void          *thread_data,
        int const     coord[2],
        int const     uv_tile[2]) const NEURAY_OVERRIDE;

    /// Handle tex::texel_float(texture_3d, ...).
    float tex_texel_float_3d(
        void const    *tex_data,
        void          *thread_data,
        int const     coord[3]) const NEURAY_OVERRIDE;

    /// Handle tex::texel_float2(texture_3d, ...).
    void tex_texel_float2_3d(
        float         result[2],
        void const    *tex_data,
        void          *thread_data,
        int const     coord[3]) const NEURAY_OVERRIDE;

    /// Handle tex::texel_float3(texture_3d, ...).
    void tex_texel_float3_3d(
        float         result[3],
        void const    *tex_data,
        void          *thread_data,
        int const     coord[3]) const NEURAY_OVERRIDE;

    /// Handle tex::texel_float4(texture_3d, ...).
    void tex_texel_float4_3d(
        float         result[4],
        void const    *tex_data,
        void          *thread_data,
        int const     coord[3]) const NEURAY_OVERRIDE;

    /// Handle tex::texel_color(texture_3d, ...).
    void tex_texel_color_3d(
        float         rgb[3],
        void const    *tex_data,
        void          *thread_data,
        int const     coord[3]) const NEURAY_OVERRIDE;

    /// Handle tex::texture_isvalid().
    ///
    /// \param tex_data  the read-only shared texture data pointer
    bool tex_isvalid(
        void const *tex_data) const NEURAY_OVERRIDE;

    /// Initializes a light profile data helper object from a given light profile tag.
    ///
    /// \param data    an 16byte aligned pointer to allocated data of at least
    ///                get_data_size() bytes
    /// \param tag     the light profile tag
    /// \param ctx     a used defined context parameter
    ///
    /// This function should create all necessary helper data for the given light profile tag
    /// and store it into the memory storage provided by \c data.
    /// This data will be passed to all light profile attribute functions as parameter \c lp_data.
    void lp_init(
        void     *data,
        unsigned tag,
        void     *ctx) NEURAY_OVERRIDE;

    /// Terminate a light profile data helper object.
    ///
    /// \param data   an 16byte aligned pointer to allocated data of at least get_data_size() bytes
    ///
    /// Clean up the helper object that was created in lp_init() here.
    void lp_term(
        void *data) NEURAY_OVERRIDE;

    /// Get the light profile power value.
    ///
    /// \param lp_data      the read-only shared light profile data pointer
    /// \param thread_data  extra per-thread data that was passed to the lambda function
    float lp_power(
        void const *lp_data,
        void       *thread_data) const NEURAY_OVERRIDE;

    /// Get the light profile maximum value.
    ///
    /// \param lp_data      the read-only shared light profile data pointer
    /// \param thread_data  extra per-thread data that was passed to the lambda function
    float lp_maximum(
        void const *lp_data,
        void       *thread_data) const NEURAY_OVERRIDE;

    /// Handle df::light_profile_isvalid().
    ///
    /// \param lp_data  the read-only shared light profile data pointer
    bool lp_isvalid(
        void const *lp_data) const NEURAY_OVERRIDE;

    /// Initializes a bsdf measurement data helper object from a given bsdf measurement tag.
    ///
    /// \param data    an 16byte aligned pointer to allocated data of at least
    ///                get_data_size() bytes
    /// \param tag     the bsdf measurement tag
    /// \param ctx     a used defined context parameter
    ///
    /// This function should create all necessary helper data for the given bsdf measurement tag
    /// and store it into the memory storage provided by \c data.
    /// This data will be passed to all bsdf measurement attribute functions as
    /// parameter \c lp_data.
    void bm_init(
        void     *data,
        unsigned tag,
        void     *ctx) NEURAY_OVERRIDE;

    /// Terminate a bsdf measurement data helper object.
    ///
    /// \param data   an 16byte aligned pointer to allocated data of at least get_data_size() bytes
    ///
    /// Clean up the helper object that was created in mp_init() here.
    void bm_term(
        void *data) NEURAY_OVERRIDE;

    /// Handle df::bsdf_measurement_isvalid().
    ///
    /// \param bm_data  the read-only shared bsdf measurement data pointer
    bool bm_isvalid(
        void const *bm_data) const NEURAY_OVERRIDE;

    /// Destructor.
    virtual ~Resource_handler();
};

}  // MDLRT
}  // MI

#endif /*RENDER_MDL_RUNTIME_I_MDLRT_RESOURCE_HANDLER_H*/

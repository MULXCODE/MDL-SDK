/******************************************************************************
 * Copyright (c) 2012-2018, NVIDIA CORPORATION. All rights reserved.
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
 *****************************************************************************/

#include "pch.h"

#include "spectral_tables.h"

namespace mi {
namespace mdl {
namespace spectral {

/* CIE standard observer color matching functions (1931)*/
const float SPECTRAL_XYZ1931_X[] = {
    0.0013680001f, 0.0022360000f, 0.0042429999f, 0.0076500000f, 0.0143100005f, 0.0231899992f,
    0.0435100012f, 0.0776299983f, 0.1343799978f, 0.2147700042f, 0.2838999927f, 0.3285000026f,
    0.3482800126f, 0.3480600119f, 0.3361999989f, 0.3186999857f, 0.2908000052f, 0.2511000037f,
    0.1953600049f, 0.1421000063f, 0.0956400037f, 0.0579500012f, 0.0320100002f, 0.0147000002f,
    0.0049000001f, 0.0024000001f, 0.0093000000f, 0.0291000009f, 0.0632700026f, 0.1096000001f,
    0.1655000001f, 0.2257499993f, 0.2903999984f, 0.3596999943f, 0.4334500134f, 0.5120499730f,
    0.5945000052f, 0.6783999801f, 0.7620999813f, 0.8424999714f, 0.9162999988f, 0.9786000252f,
    1.0262999535f, 1.0566999912f, 1.0621999502f, 1.0456000566f, 1.0025999546f, 0.9383999705f,
    0.8544499874f, 0.7513999939f, 0.6424000263f, 0.5418999791f, 0.4478999972f, 0.3607999980f,
    0.2834999859f, 0.2187000066f, 0.1649000049f, 0.1212000027f, 0.0873999968f, 0.0636000037f,
    0.0467699990f, 0.0329000019f, 0.0227000006f, 0.0158399995f, 0.0113589996f, 0.0081110001f,
    0.0057899999f, 0.0041089999f, 0.0028990000f, 0.0020490000f, 0.0014400000f, 0.0010000000f,
    0.0006900000f, 0.0004760000f, 0.0003320000f, 0.0002350000f, 0.0001660000f, 0.0001170000f,
    0.0000830000f, 0.0000590000f, 0.0000420000f};
const float SPECTRAL_XYZ1931_Y[] = {
    0.0000390000f, 0.0000640000f, 0.0001200000f, 0.0002170000f, 0.0003960000f, 0.0006400000f,
    0.0012100000f, 0.0021800001f, 0.0040000002f, 0.0073000002f, 0.0115999999f, 0.0168399997f,
    0.0230000000f, 0.0297999997f, 0.0379999988f, 0.0480000004f, 0.0599999987f, 0.0738999993f,
    0.0909800008f, 0.1125999987f, 0.1390199959f, 0.1693000048f, 0.2080200016f, 0.2585999966f,
    0.3230000138f, 0.4072999954f, 0.5030000210f, 0.6082000136f, 0.7099999785f, 0.7932000160f,
    0.8619999886f, 0.9148499966f, 0.9539999962f, 0.9803000093f, 0.9949499965f, 1.0000000000f,
    0.9950000048f, 0.9786000252f, 0.9520000219f, 0.9154000282f, 0.8700000048f, 0.8162999749f,
    0.7570000291f, 0.6948999763f, 0.6309999824f, 0.5667999983f, 0.5030000210f, 0.4411999881f,
    0.3810000122f, 0.3210000098f, 0.2649999857f, 0.2169999927f, 0.1749999970f, 0.1381999999f,
    0.1070000008f, 0.0816000029f, 0.0610000007f, 0.0445800014f, 0.0320000015f, 0.0231999997f,
    0.0170000009f, 0.0119200004f, 0.0082099997f, 0.0057230000f, 0.0041020000f, 0.0029290000f,
    0.0020910001f, 0.0014840000f, 0.0010470001f, 0.0007400000f, 0.0005200000f, 0.0003610000f,
    0.0002490000f, 0.0001720000f, 0.0001200000f, 0.0000850000f, 0.0000600000f, 0.0000420000f,
    0.0000300000f, 0.0000210000f, 0.0000150000f};
const float SPECTRAL_XYZ1931_Z[] = {
    0.0064500002f, 0.0105499998f, 0.0200500004f, 0.0362100005f, 0.0678500012f, 0.1102000028f,
    0.2073999941f, 0.3713000119f, 0.6456000209f, 1.0390499830f, 1.3855999708f, 1.6229599714f,
    1.7470599413f, 1.7826000452f, 1.7721099854f, 1.7440999746f, 1.6691999435f, 1.5281000137f,
    1.2876399755f, 1.0419000387f, 0.8129500151f, 0.6161999702f, 0.4651800096f, 0.3533000052f,
    0.2720000148f, 0.2123000026f, 0.1581999958f, 0.1116999984f, 0.0782499984f, 0.0572500005f,
    0.0421600007f, 0.0298400000f, 0.0203000009f, 0.0133999996f, 0.0087500000f, 0.0057500000f,
    0.0038999999f, 0.0027500000f, 0.0020999999f, 0.0018000000f, 0.0016500000f, 0.0014000000f,
    0.0011000000f, 0.0010000000f, 0.0008000000f, 0.0006000000f, 0.0003400000f, 0.0002400000f,
    0.0001900000f, 0.0001000000f, 0.0000500000f, 0.0000300000f, 0.0000200000f, 0.0000100000f,
    0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f,
    0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f,
    0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f,
    0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f,
    0.0000000000f, 0.0000000000f, 0.0000000000f};

#if 0
/* CIE standard observer color matching functions (1964)*/
const float SPECTRAL_XYZ1964_X[] = {
    0.0001600000f, 0.0006620000f, 0.0023620001f, 0.0072420002f, 0.0191099998f, 0.0434000008f, 
    0.0847359970f, 0.1406379938f, 0.2044920027f, 0.2647370100f, 0.3146789968f, 0.3577190042f, 
    0.3837339878f, 0.3867259920f, 0.3707019985f, 0.3429569900f, 0.3022730052f, 0.2540850043f, 
    0.1956180036f, 0.1323489994f, 0.0805070028f, 0.0410719998f, 0.0161719993f, 0.0051320000f, 
    0.0038160000f, 0.0154440003f, 0.0374649987f, 0.0713580027f, 0.1177489981f, 0.1729529947f,
    0.2364909947f, 0.3042129874f, 0.3767719865f, 0.4515840113f, 0.5298259854f, 0.6160529852f,
    0.7052239776f, 0.7938320041f, 0.8786550164f, 0.9511619806f, 1.0141600370f, 1.0743000507f, 
    1.1185200214f, 1.1342999935f, 1.1239900589f, 1.0891000032f, 1.0304800272f, 0.9507399797f, 
    0.8562970161f, 0.7549300194f, 0.6474670172f, 0.5351099968f, 0.4315670133f, 0.3436900079f, 
    0.2683289945f, 0.2043000013f, 0.1525679976f, 0.1122099981f, 0.0812610015f, 0.0579300001f,
    0.0408510007f, 0.0286229998f, 0.0199410003f, 0.0138419997f, 0.0095769996f, 0.0066049998f,
    0.0045530000f, 0.0031450000f, 0.0021750000f, 0.0015059999f, 0.0010450000f, 0.0007270000f, 
    0.0005080000f, 0.0003560000f, 0.0002510000f, 0.0001780000f, 0.0001260000f, 0.0000900000f, 
    0.0000650000f, 0.0000460000f, 0.0000330000f};
const float SPECTRAL_XYZ1964_Y[] = {
    0.0000170000f, 0.0000720000f, 0.0002530000f, 0.0007690000f, 0.0020039999f, 0.0045090001f, 
    0.0087559996f, 0.0144560002f, 0.0213910006f, 0.0294969995f, 0.0386760011f, 0.0496019982f,
    0.0620770007f, 0.0747039989f, 0.0894559994f, 0.1062560007f, 0.1282009929f, 0.1527609974f,
    0.1851900071f, 0.2199400067f, 0.2535890043f, 0.2976650000f, 0.3391329944f, 0.3953790069f, 
    0.4607770145f, 0.5313599706f, 0.6067410111f, 0.6856600046f, 0.7617570162f, 0.8233299851f,
    0.8752110004f, 0.9238100052f, 0.9619879723f, 0.9822000265f, 0.9917610288f, 0.9991099834f, 
    0.9973400235f, 0.9823799729f, 0.9555519819f, 0.9151750207f, 0.8689339757f, 0.8256229758f, 
    0.7774050236f, 0.7203530073f, 0.6583409905f, 0.5938779712f, 0.5279629827f, 0.4618340135f,
    0.3980570138f, 0.3395540118f, 0.2834930122f, 0.2282540053f, 0.1798280030f, 0.1402110010f, 
    0.1076330021f, 0.0811870024f, 0.0602810010f, 0.0440960005f, 0.0318000019f, 0.0226019993f, 
    0.0159050003f, 0.0111300005f, 0.0077490001f, 0.0053750002f, 0.0037179999f, 0.0025650000f, 
    0.0017680000f, 0.0012220000f, 0.0008460000f, 0.0005860000f, 0.0004070000f, 0.0002840000f, 
    0.0001990000f, 0.0001400000f, 0.0000980000f, 0.0000700000f, 0.0000500000f, 0.0000360000f, 
    0.0000250000f, 0.0000180000f, 0.0000130000f};
const float SPECTRAL_XYZ1964_Z[] = {
    0.0007050000f, 0.0029279999f, 0.0104820002f, 0.0323439986f, 0.0860110000f, 0.1971199960f,
    0.3893660009f, 0.6567599773f, 0.9725419879f, 1.2825000286f, 1.5534800291f, 1.7984999418f,
    1.9672800303f, 2.0272998810f, 1.9947999716f, 1.9006999731f, 1.7453700304f, 1.5549000502f,
    1.3175599575f, 1.0302000046f, 0.7721250057f, 0.5700600147f, 0.4152539968f, 0.3023560047f,
    0.2185020000f, 0.1592489928f, 0.1120439991f, 0.0822480023f, 0.0607089996f, 0.0430499986f,
    0.0304509997f, 0.0205840003f, 0.0136759998f, 0.0079180002f, 0.0039880001f, 0.0010910000f,
    0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f,
    0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f,
    0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f,
    0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f,
    0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f,
    0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f,
    0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f, 0.0000000000f,
    0.0000000000f, 0.0000000000f, 0.0000000000f};
#endif

const float D60[SPECTRAL_XYZ_RES] = {
    41.1939622845311f, 43.7996495741081f, 46.4053443694044f, 59.2495668772834f,
    72.0937893734314f, 76.1604005037247f, 80.2270095879923f, 81.4725118293678f,
    82.7180196233373f, 80.1213189543133f, 77.5246259457215f, 86.5451852785837f,
    95.5657542869197f,101.7081387279023f,107.8505211229663f,108.6595358061121f,
   109.4685429835387f,108.5770405324361f,107.6855389805656f,108.6509486391944f,
   109.6163593208360f,106.6350700543170f,103.6537816869229f,104.4217965388071f,
   105.1898027381265f,104.7924104156134f,104.3950252110957f,103.4526535006373f,
   102.5102812786188f,104.2788070205345f,106.0473325067221f,104.6771051706626f,
   103.3068780903832f,103.4217635190818f,103.5366566411065f,101.7683245058292f,
   100.0000000000000f, 98.3771714612798f, 96.7543429225596f, 96.7360183925496f,
    96.7176862891862f, 93.3024888291968f, 89.8872913692075f, 90.9186373938613f,
    91.9499759127423f, 91.9918659750474f, 92.0337561611333f, 91.3034898296861f,
    90.5732313752485f, 88.5107796925075f, 86.4483358868298f, 86.9585785011902f,
    87.4688137335067f, 85.6594825178889f, 83.8501507908184f, 84.2114221156823f,
    84.5726924341244f, 85.9476350700216f, 87.3225772110033f, 85.3115072039523f,
    83.3004448264548f, 78.6644159193148f, 74.0283946417285f, 75.2396639291860f,
    76.4509408627346f, 77.6791169718379f, 78.9073001988292f, 72.1297552280172f,
    65.3522140720051f, 69.6646851424460f, 73.9771526456446f, 76.6842559206226f,
    79.3913599546182f, 73.2923675079999f, 67.1933750613297f, 58.1890199083549f,
    49.1846609406801f, 59.9755410371265f, 70.7664175661787f, 68.9075859336080f,
    67.0487459125749f};

const float D65[SPECTRAL_XYZ_RES] = {
    49.9754981995000f, 52.3117980957000f, 54.6482009888000f, 68.7014999390000f,
    82.7548980713000f, 87.1203994751000f, 91.4860000610000f, 92.4589004517000f,
    93.4318008423000f, 90.0569992065000f, 86.6822967529000f, 95.7735977173000f,
   104.8649978638000f,110.9359970093000f,117.0080032349000f,117.4100036621000f,
   117.8119964600000f,116.3359985352000f,114.8610000610000f,115.3919982910000f,
   115.9229965210000f,112.3669967651000f,108.8109970093000f,109.0820007324000f,
   109.3539962769000f,108.5780029297000f,107.8020019531000f,106.2959976196000f,
   104.7900009155000f,106.2389984131000f,107.6890029907000f,106.0469970703000f,
   104.4049987793000f,104.2249984741000f,104.0459976196000f,102.0230026245000f,
   100.0000000000000f, 98.1670989990000f, 96.3341979980000f, 96.0610961914000f,
    95.7880020142000f, 92.2368011475000f, 88.6856002808000f, 89.3459014893000f,
    90.0062026978000f, 89.8025970459000f, 89.5990982056000f, 88.6489028931000f,
    87.6986999512000f, 85.4935989380000f, 83.2885971069000f, 83.4938964844000f,
    83.6992034912000f, 81.8629989624000f, 80.0268020630000f, 80.1206970215000f,
    80.2145996094000f, 81.2462005615000f, 82.2778015137000f, 80.2809982300000f,
    78.2842025757000f, 74.0027008057000f, 69.7212982178000f, 70.6651992798000f,
    71.6091003418000f, 72.9789962769000f, 74.3489990234000f, 67.9765014648000f,
    61.6040000916000f, 65.7447967529000f, 69.8855972290000f, 72.4862976074000f,
    75.0869979858000f, 69.3397979736000f, 63.5927009583000f, 55.0054016113000f,
    46.4182014465000f, 56.6118011475000f, 66.8053970337000f, 65.0941009521000f,
    63.3828010559000f};


const float srgb_relative_s001[SPECTRAL_XYZ_RES] = {
    0.7019792349932337f, 0.6846481206398503f, 0.7130972973175185f, 0.73266714528591f,
    0.7521753527278733f, 0.7709287265054129f, 0.789839815385755f, 0.8235606525250434f,
    0.8786107875615614f, 0.9819578876471478f, 0.9910198164593675f, 0.9950480136097326f,
    0.9436353765848104f, 0.9998792177404764f, 0.8488676690307428f, 0.9961770321993882f,
    0.819092009947177f, 0.8693280726453727f, 0.9359223559126267f, 0.9802148013732643f,
    0.9873919496528827f, 0.762498683698901f, 0.5875320200030119f, 0.4455357629379469f,
    0.3232452860337242f, 0.2146231663481411f, 0.1105830203391148f, 0.0023782638867893f,
    8.907415964553439e-05f, 0.001459913011225042f, 0.000932672955839528f, 0.000332958270090708f,
    5.026192962762771e-05f, 0.0005468218660104641f, 7.520923086520859e-06f, 0.000885416183660951f,
    -1.19178209634363e-07f, 0.0007289616144523989f, 0.000326890655394145f, 0.001424896636224957f,
    0.0003527845099592017f, -8.012812441338113e-09f, 0.0009917620535089787f, 1.245433710223703e-05f,
    0.022436988878166f, 0.03782700617187142f, 0.04913846245879957f, 0.05246541472255685f,
    0.0529704236704063f, 0.05254462732520614f, 0.04843639157899395f, 0.03970815158454097f,
    0.03664607804454036f, 0.03154054908408425f, 0.02478502138590596f, 0.01393860143108826f,
    0.009836566488988556f, 0.01147597456619223f, 0.007181309279230294f, 0.004978538278526919f,
    0.006539008248039237f, 0.01095034160017993f, 0.0109789375214253f, 0.01409519276126715f,
    0.01862123601479276f, 0.02041807717078808f, 0.01884598225610058f, 0.01844385324779113f,
    0.01781522663191143f, 0.01833787401095953f, 0.01832286864208541f, 0.01710461264404163f,
    0.01443757237003768f, 0.01175290346527167f, 0.01065350510302022f, 0.009188972800416986f,
    0.008063881046835971f, 0.005098166251734971f, 5.422131514926884e-05f, 0.002542644119214575f,
    0.002116346517627834f};

const float srgb_relative_s010[SPECTRAL_XYZ_RES] = {
    0.002428537529314051f, 6.788575489867908e-05f, 6.725626688651855e-05f, 2.780309549871995e-05f,
    0.0001642419921234072f, 5.763471518867129e-06f, 5.392158138202386e-05f, 5.633821650198947e-05f,
    0.001085841124899043f, 0.001542727200739068f, 0.001755915747138698f, 0.002978211441831637f,
    0.006060253896220232f, 0.003772278489164609f, 0.002326931076834186f, 0.003654542281162972f,
    0.02285080189212957f, 0.002708705188365274f, 0.1104034162421462f, 0.2133837707508288f,
    0.300326370173519f, 0.3959033734614398f, 0.4892826946021689f, 0.5993517446694732f,
    0.7121688716618624f, 0.8435459116087931f, 0.9938065493525754f, 1.000001235762447f,
    0.9992469168279198f, 0.9915923757631233f, 0.9909168538280776f, 0.9996072617681397f,
    0.937281181520349f, 0.9317232523774757f, 0.9883561064022359f, 0.9922479572295444f,
    0.9941673691633653f, 0.9985359085448036f, 0.9878459218067155f, 0.8322731621066195f,
    0.6984117028125799f, 0.5727468209020763f, 0.4692579042443153f, 0.3730414922792309f,
    0.280613551850835f, 0.1946980728242398f, 0.1082447267895803f, 0.02520999283290681f,
    0.006141589723264229f, 0.001013331676766215f, 0.001443509543830193f, 0.004209544629105652f,
    0.001405712097424739f, 0.001973862631341417f, 0.05136508935635808f, 3.163895405110858e-05f,
    0.0001260002231503179f, 4.783931540578573e-07f, 0.001283808690240014f, 4.453436854069161e-07f,
    8.693190387596512e-05f, 5.828184541748892e-05f, 3.404341008510898e-05f, 7.792065213889864e-05f,
    6.24850801866107e-05f, 6.203694436050002e-05f, 0.0002714203171743757f, 4.270219312287799e-05f,
    0.0008897247523153642f, 0.0001024151643443927f, 5.259823329273516e-05f, 2.389690630557454e-05f,
    7.149778971355259e-05f, 6.0800633311615e-05f, 0.0001404541923251892f, 0.0005937210299316007f,
    3.088735749824894e-05f, 6.35367462307171e-06f, 0.0006393304224797922f, 0.01346534081537606f,
    0.01917413941812931f};

const float srgb_relative_s011[SPECTRAL_XYZ_RES] = {
    0.9852372687657427f, 0.9846461448598636f, 0.9842181168286804f, 0.9820795718731994f,
    0.980908895691984f, 0.9806632318681796f, 0.983496790349518f, 0.9698103528752705f,
    0.9999942309347318f, 0.9902332330378104f, 0.980671310124241f, 0.9997821728218059f,
    0.9998435958874569f, 0.9637050530712068f, 0.9819268206703333f, 0.9580966578157672f,
    0.9861377896731414f, 0.98039475475582f, 0.9900915548710708f, 0.9960395156653334f,
    0.9679930768852574f, 0.9703363170988208f, 0.9881077374359308f, 0.9860523177565927f,
    0.9818462586206771f, 0.98141110425357f, 0.9864619138129831f, 0.9999430993926f,
    0.9948758896915102f, 0.9990386938270237f, 0.9747010523347619f, 0.9821749791741461f,
    0.9699863670717512f, 0.9711202022392692f, 0.9739864797102679f, 0.9923676996500138f,
    0.9739053096311008f, 0.9578995081865905f, 0.9598141779686484f, 0.977596207801394f,
    0.9791296522933828f, 0.9997606161795909f, 0.6462254092564765f, 0.3175132325090445f,
    0.004523671684868114f, 0.002502457341269776f, 0.001233459757027489f, 0.000936083629012735f,
    0.002646736908561008f, 0.004442677337263667f, 0.0003693672074181718f, 1.647397357418257e-10f,
    0.004929919926435872f, 0.004852191496855301f, 0.00180880598553168f, 0.0009583177383734065f,
    0.003334066177884495f, 0.0029070809420053f, 0.0009951298711094784f, 0.0001915726723507745f,
    0.00407679894708919f, 0.006079228740884422f, 0.008546938247397044f, 0.008327999812784568f,
    0.01044950849066689f, 0.00860578763189987f, 0.01043024314890605f, 0.008169598743991447f,
    0.009146838075391751f, 0.00713403189306838f, 0.007255173568464483f, 0.005702724361243096f,
    0.005162330311683921f, 0.004036826019850519f, 0.003332656635873184f, 0.002554748804969853f,
    0.001942155644468927f, 0.001522783667325949f, 0.001139008439336342f, 0.0009492905384319335f,
    0.0008275735558370947f};

const float srgb_relative_s100[SPECTRAL_XYZ_RES] = {
    0.0007409220676516125f, 0.004849830418717687f, 0.001842751401660805f, 0.007147352338464253f,
    0.002019158696403484f, 0.003399533567782214f, 0.005118727330893039f, 0.01436073227948874f,
    0.002419732549565436f, 0.01418418901778661f, 0.003728704086479323f, 0.003051349822643837f,
    0.006183308407595969f, 0.007974818904756625f, 0.01049069043626785f, 0.02332968717302015f,
    0.01047712451887445f, 0.001501131209837158f, 0.006241064560863381f, 0.005919984587085966f,
    0.01255884422334294f, 0.1993577551512564f, 0.1563219533493726f, 9.217926200122406e-09f,
    0.00137385336296364f, 0.004067686225423722f, 0.008848539328186855f, 0.01771450860144669f,
    0.0006550149504790936f, 0.04564819791631125f, 0.0005973170963574637f, 0.01157964800558073f,
    0.001793711467677789f, 0.01844966493138794f, 0.008534775177902874f, 0.01302599042800331f,
    0.009637548915778088f, 0.04437545679889537f, 0.02017691805169797f, 0.05806322380947027f,
    0.03139649449404591f, 0.006782877013468136f, 0.01850192015876473f, 1.001180576302825f,
    1.004041261789702f, 1.005840378008476f, 1.001013576582545f, 1.000120028586126f,
    1.002787210417777f, 1.00199084532196f, 0.9989448506546621f, 0.9949326704045063f,
    0.996205638445032f, 1.001897631835025f, 1.001521715477919f, 1.000566593664006f,
    0.9964151908264555f, 0.9894564557816521f, 0.9911424364083202f, 0.9697669641242773f,
    0.9874082114233729f, 0.9951578595580749f, 0.9740327270229423f, 0.9791985776406157f,
    0.9994266731163705f, 1.003316424976203f, 0.7629036447514228f, 0.5329690363217223f,
    0.3670684680826211f, 0.2566466651644825f, 0.1823105116309411f, 0.1303484789186605f,
    0.09227206861235453f, 0.06321385581926865f, 0.04203572740819442f, 0.0273487439689453f,
    0.01793053684638936f, 0.01253976251611535f, 0.00928451372181338f, 0.007160666338817392f,
    0.00602276013321131f};

const float srgb_relative_s101[SPECTRAL_XYZ_RES] = {
    0.03966424360978084f, 0.0666842669979759f, 0.1360126372165655f, 0.2971177379492205f,
    0.6035414481466175f, 0.9604698342966149f, 0.9961111272763699f, 0.9893097234761996f,
    0.9790692122822285f, 0.9851651899109966f, 0.999999996531761f, 0.9998209398606008f,
    0.9980340098084008f, 0.9997635473018051f, 0.9938224951813093f, 0.9993339721766316f,
    0.999904227363565f, 0.9980040890818495f, 0.9999325874316333f, 0.9984926086588051f,
    0.9991469943857181f, 0.0008135094923077957f, 0.03460074425022895f, 0.002309867592728061f,
    0.5218622061089874f, 0.0009286292974522437f, 0.4249726437829449f, 0.2864387932040004f,
    1.395450039132218e-06f, 0.0005263805378643016f, 0.02020544774928343f, 0.001656886053709783f,
    0.0005813948547832987f, 0.0008397357404892978f, 0.01208138694789209f, 0.0649510446178299f,
    0.02045289273519157f, 0.0009498973779616948f, 0.035448624429127f, 0.0008299230684262193f,
    0.001662311966121321f, 0.002062681203665928f, 0.9349351684727306f, 0.9964466864906643f,
    0.9048723983685156f, 0.991621724066827f, 0.9636433895989418f, 0.9184728713334172f,
    0.8288598907749665f, 0.9932109191470992f, 0.9512612373755814f, 0.9413027178685172f,
    0.9441527171417219f, 0.9615074164960868f, 0.9702440264806318f, 0.9675526946187083f,
    0.9911763458230497f, 0.9299073733355203f, 0.7039599622841168f, 0.508576178361903f,
    0.3625286331688867f, 0.2461308619590631f, 0.1634964918146734f, 0.1137658593769352f,
    0.08179347675587997f, 0.05930370101535327f, 0.04254910835403532f, 0.02846534673463662f,
    0.01873930431404859f, 0.01352658514667865f, 0.009998525028822347f, 0.007271355044460738f,
    0.005155246536688316f, 0.003363287960474204f, 0.002150347422884713f, 0.001352280895826105f,
    0.0008289800665591715f, 0.0006540553970425129f, 0.0005142962893266951f, 0.0003910890502297751f,
    0.0002902010637260777f};

const float srgb_relative_s110[SPECTRAL_XYZ_RES] = {
    0.2322510131596014f, 0.2338053649341241f, 0.2305391334750355f, 0.2240444825302954f,
    0.222290950620112f, 0.2190033756545315f, 0.2112729916051158f, 0.2036218909071616f,
    0.1944355163449629f, 0.1838858465678188f, 0.1692374684140473f, 0.1440249952295104f,
    0.1141703026730981f, 0.0828879074816061f, 0.04345924010348871f, 1.119134705546143e-06f,
    0.0001354503969870913f, 0.0001498310029654226f, 5.626623085494553e-06f, 7.71358463214078e-10f,
    1.211763175967828e-06f, 0.2022857130064065f, 0.3995860977711797f, 0.5943020896119411f,
    0.7741579535977097f, 0.9520321516189659f, 0.9940615250215923f, 0.9933115010271515f,
    0.9942523021512848f, 0.9877539267090167f, 0.9932153305868361f, 0.9943442666382879f,
    0.9883384138810725f, 0.9881696929910966f, 0.9856156539578474f, 0.9842044355170503f,
    0.9890423933794129f, 0.9768486236609222f, 0.9682982479615889f, 0.9896401562297059f,
    0.9886085130157716f, 0.974561811337312f, 0.9952720520794776f, 0.9964823787510263f,
    0.9787564547167399f, 0.9816676253894546f, 0.95277294659181f, 0.9632527644893615f,
    0.959762550690106f, 0.9997641361779183f, 0.9730804694801571f, 0.9849302183589388f,
    0.9812787815901709f, 0.987263388006969f, 0.9979069536466842f, 0.9999880057301322f,
    0.9958804110904349f, 0.9902337154682648f, 0.9948438379481567f, 0.9648758292879309f,
    0.9240360398987943f, 0.8840765095223057f, 0.8404526340004388f, 0.7958322238012531f,
    0.7634595178216689f, 0.7234047109580162f, 0.6843540312649222f, 0.652787251042751f,
    0.6262623429713907f, 0.5950317233987727f, 0.5678228727842928f, 0.5340687103718186f,
    0.5016722470544752f, 0.4567691233785649f, 0.4067748059137121f, 0.3387787400013262f,
    0.2813882684603767f, 0.2455242826762348f, 0.1966594839904222f, 0.1578683035764035f,
    0.1365928227215609f};


} // namespace spectral
} // namespace mdl
} // namespace mi

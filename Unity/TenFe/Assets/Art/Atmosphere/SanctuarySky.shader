Shader "TenFe/Sanctuary Sky"
{
    Properties
    {
        _Zenith ("Night sky", Color) = (.018,.036,.07,1)
        _Horizon ("Horizon haze", Color) = (.23,.29,.32,1)
        _Cloud ("Clouds", Color) = (.085,.11,.15,1)
    }
    SubShader
    {
        Tags { "Queue"="Background" "RenderType"="Background" "PreviewType"="Skybox" }
        Cull Off ZWrite Off
        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"
            struct v2f { float4 pos : SV_POSITION; float3 direction : TEXCOORD0; };
            float4 _Zenith, _Horizon, _Cloud;
            v2f vert(appdata_base v) { v2f o; o.pos = UnityObjectToClipPos(v.vertex); o.direction = v.vertex.xyz; return o; }
            float hash(float2 p) { return frac(sin(dot(p,float2(127.1,311.7)))*43758.5453); }
            float noise(float2 p)
            {
                float2 i=floor(p), f=frac(p); f=f*f*(3-2*f);
                return lerp(lerp(hash(i),hash(i+float2(1,0)),f.x),lerp(hash(i+float2(0,1)),hash(i+1),f.x),f.y);
            }
            float4 frag(v2f i) : SV_Target
            {
                float3 d=normalize(i.direction);
                float h=saturate(d.y);
                float3 sky=lerp(_Horizon.rgb,_Zenith.rgb,pow(h,.45));
                float2 p=d.xz/(max(.12,h)+.15)*2.2 + float2(_Time.y*.003,0);
                float clouds=noise(p)*.55 + noise(p*2.07)*.28 + noise(p*4.13)*.17;
                float cover=smoothstep(.43,.72,clouds)*smoothstep(0,.16,h);
                sky=lerp(sky,_Cloud.rgb,cover*.7);
                // Broad warm scattering behind the physical eclipse, without a second sun disc.
                float halo=pow(saturate(dot(d,normalize(float3(0,.28,1)))),22);
                sky+=float3(.18,.077,.025)*halo*(1-cover*.65);
                return float4(sky,1);
            }
            ENDCG
        }
    }
    Fallback Off
}

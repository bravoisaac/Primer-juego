Shader "TenFe/Weathered Stone"
{
    Properties
    {
        _Color ("Stone", Color) = (.24,.28,.3,1)
        _Patina ("Mineral deposits", Color) = (.13,.19,.18,1)
        _Metallic ("Metal", Range(0,1)) = .05
        _Glossiness ("Polish", Range(0,1)) = .3
        _Relief ("Surface relief", Range(0,.2)) = .045
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        LOD 200
        CGPROGRAM
        #pragma surface surf Standard fullforwardshadows
        #pragma target 3.0
        #include "UnityCG.cginc"
        struct Input { float3 worldPos; float3 worldNormal; INTERNAL_DATA };
        float4 _Color, _Patina;
        float _Metallic, _Glossiness, _Relief;
        float hash(float3 p) { return frac(sin(dot(p,float3(127.1,311.7,74.7)))*43758.5453); }
        float noise(float3 p)
        {
            float3 i=floor(p), f=frac(p); f=f*f*(3-2*f);
            return lerp(lerp(lerp(hash(i),hash(i+float3(1,0,0)),f.x),lerp(hash(i+float3(0,1,0)),hash(i+float3(1,1,0)),f.x),f.y),
                        lerp(lerp(hash(i+float3(0,0,1)),hash(i+float3(1,0,1)),f.x),lerp(hash(i+float3(0,1,1)),hash(i+1),f.x),f.y),f.z);
        }
        void surf(Input IN, inout SurfaceOutputStandard o)
        {
            // World coordinates keep grain at the same scale on floor tiles, columns and tall walls.
            float broad=noise(IN.worldPos*1.7);
            float grain=noise(IN.worldPos*24);
            float vein=pow(saturate(1-abs(broad-.48)*14),5);
            float h=broad*.65 + grain*.18 - vein*.1;
            float stains=smoothstep(.48,.76,noise(IN.worldPos*.48));
            float3 color=lerp(_Color.rgb,_Patina.rgb,stains*.5);
            o.Albedo=color*(.65 + broad*.6 + grain*.22)*(1-vein*.28);
            o.Metallic=_Metallic;
            o.Smoothness=saturate(_Glossiness+(broad-.5)*.2);
            o.Occlusion=1-vein*.16;
            float3 n=normalize(WorldNormalVector(IN,float3(0,0,1)));
            float3 dx=ddx(IN.worldPos), dy=ddy(IN.worldPos);
            float3 r1=cross(dy,n), r2=cross(n,dx);
            float det=dot(dx,r1);
            float3 gradient=(ddx(h)*r1+ddy(h)*r2)*sign(det)/max(abs(det),.00001);
            float3 detail=normalize(n-gradient*_Relief);
            o.Normal=normalize(float3(dot(detail,WorldNormalVector(IN,float3(1,0,0))),dot(detail,WorldNormalVector(IN,float3(0,1,0))),dot(detail,n)));
        }
        ENDCG
    }
    Fallback "Standard"
}

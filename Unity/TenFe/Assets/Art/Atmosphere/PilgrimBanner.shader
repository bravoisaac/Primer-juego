Shader "TenFe/Pilgrim Banner"
{
    Properties
    {
        _Color ("Ocaso cloth", Color) = (.24,.065,.055,1)
        _Trim ("Woven gold", Color) = (.52,.34,.12,1)
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        Cull Off
        CGPROGRAM
        #pragma surface surf Standard fullforwardshadows vertex:vert addshadow
        #pragma target 3.0
        struct Input { float2 bannerUV; float facing : VFACE; };
        float4 _Color, _Trim;
        void vert(inout appdata_full v, out Input o)
        {
            UNITY_INITIALIZE_OUTPUT(Input,o);
            o.bannerUV=v.texcoord.xy;
            float free=pow(1-v.texcoord.y,2);
            float phase=mul(unity_ObjectToWorld,v.vertex).x*.7 + _Time.y*1.6;
            v.vertex.z+=(sin(phase+v.vertex.y*2.2)*.16+sin(phase*1.7+v.vertex.y*3.1)*.06)*free;
            v.vertex.x+=sin(phase*.7+v.vertex.y)*.055*free;
        }
        void surf(Input IN, inout SurfaceOutputStandard o)
        {
            float2 uv=IN.bannerUV;
            float border=1-smoothstep(.045,.065,min(uv.x,1-uv.x));
            float seal=1-smoothstep(.016,.025,abs(length((uv-float2(.5,.67))*float2(1,2.5))-.23));
            float stem=(1-smoothstep(.018,.026,abs(uv.x-.5)))*step(.35,uv.y)*step(uv.y,.83);
            float weave=.94+.06*sin(uv.x*650)*sin(uv.y*1200);
            o.Albedo=lerp(_Color.rgb,_Trim.rgb,saturate(border+seal+stem))*weave;
            o.Normal=float3(0,0,IN.facing >= 0 ? 1 : -1);
            o.Smoothness=.15; o.Metallic=.05;
        }
        ENDCG
    }
    Fallback "Standard"
}

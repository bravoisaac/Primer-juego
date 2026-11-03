Shader "TenFe/Sacred Fire"
{
    SubShader
    {
        Tags { "Queue"="Transparent" "RenderType"="Transparent" "IgnoreProjector"="True" }
        Blend SrcAlpha One
        Cull Off Lighting Off ZWrite Off
        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile_fog
            #include "UnityCG.cginc"
            struct appdata { float4 vertex:POSITION; float4 color:COLOR; float2 uv:TEXCOORD0; };
            struct v2f { float4 pos:SV_POSITION; float4 color:COLOR; float2 uv:TEXCOORD0; UNITY_FOG_COORDS(1) };
            v2f vert(appdata v) { v2f o; o.pos=UnityObjectToClipPos(v.vertex); o.uv=v.uv; o.color=v.color; UNITY_TRANSFER_FOG(o,o.pos); return o; }
            float4 frag(v2f i):SV_Target
            {
                float2 p=i.uv*2-1;
                float alpha=pow(saturate(1-dot(p,p)),2);
                float4 c=float4(i.color.rgb,i.color.a*alpha);
                UNITY_APPLY_FOG_COLOR(i.fogCoord,c,float4(0,0,0,0));
                return c;
            }
            ENDCG
        }
    }
    Fallback Off
}

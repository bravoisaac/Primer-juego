Shader "Hidden/TenFe/Sanctuary Grade"
{
    Properties { _MainTex ("Scene", 2D) = "white" {} _BloomTex ("Bloom", 2D) = "black" {} }
    SubShader
    {
        Cull Off ZWrite Off ZTest Always
        CGINCLUDE
        #include "UnityCG.cginc"
        sampler2D _MainTex, _BloomTex;
        float4 _MainTex_TexelSize;
        float2 _BlurDirection;
        float _BloomStrength, _Vignette;
        float4 extract(v2f_img i):SV_Target
        {
            float3 c=tex2D(_MainTex,i.uv).rgb;
            float brightness=max(c.r,max(c.g,c.b));
            return float4(c*max(0,brightness-.85)/max(.001,brightness),1);
        }
        float4 blur(v2f_img i):SV_Target
        {
            float2 offset=_MainTex_TexelSize.xy*_BlurDirection;
            float3 c=tex2D(_MainTex,i.uv).rgb*.227027;
            c+=(tex2D(_MainTex,i.uv+offset*1.384615).rgb+tex2D(_MainTex,i.uv-offset*1.384615).rgb)*.316216;
            c+=(tex2D(_MainTex,i.uv+offset*3.230769).rgb+tex2D(_MainTex,i.uv-offset*3.230769).rgb)*.070270;
            return float4(c,1);
        }
        float4 grade(v2f_img i):SV_Target
        {
            float2 bloomUV=i.uv;
            #if UNITY_UV_STARTS_AT_TOP
            if (_MainTex_TexelSize.y < 0) bloomUV.y=1-bloomUV.y;
            #endif
            float3 c=tex2D(_MainTex,i.uv).rgb+tex2D(_BloomTex,bloomUV).rgb*_BloomStrength;
            // A gentle shoulder preserves bright fire and readable metal without clipping to white.
            c=c*(1+c/4)/(1+c);
            float2 p=i.uv*2-1;
            c*=1-_Vignette*smoothstep(.35,1.5,dot(p,p));
            return float4(c,1);
        }
        ENDCG
        Pass
        {
            CGPROGRAM
            #pragma vertex vert_img
            #pragma fragment extract
            ENDCG
        }
        Pass
        {
            CGPROGRAM
            #pragma vertex vert_img
            #pragma fragment blur
            ENDCG
        }
        Pass
        {
            CGPROGRAM
            #pragma vertex vert_img
            #pragma fragment grade
            ENDCG
        }
    }
    Fallback Off
}

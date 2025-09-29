import streamlit as st
from checker import analyze_claim_with_openrouter
from retriever import retrieve_all_sources

st.set_page_config(page_title="Wikipedia Fact Checker", page_icon="✅")

st.title("🔍Fact Checker")
st.write("Enter a claim below and I'll check it against live Wikipedia summaries and Google Fact Check using an LLM.")

# User input
claim = st.text_input("**Enter a factual claim:**")

if st.button("✅ Check Claim") and claim:
    with st.spinner("Retrieving evidence and analyzing..."):
        try:
            all_sources = retrieve_all_sources(claim)  # new function returning dict

            result = analyze_claim_with_openrouter(claim, all_sources)  # updated to take dict
            st.success("✅ Analysis Complete!")

            import json
            result_data = json.loads(result)

            st.markdown(f"### Verdict: `{result_data['verdict']}`")
            st.markdown(f"**Explanation:** {result_data['explanation']}")
            st.markdown(f"**Confidence:** {result_data.get('confidence', 'N/A')}")

            if "follow_up" in result_data and result_data["follow_up"].strip():
                st.markdown(f"**Follow-up Answer:** {result_data['follow_up']}")

            st.markdown("### 📚 Sources Used:")
            for source_name, items in all_sources.items():
                st.markdown(f"**{source_name}**")
                for entry in items:
                    st.markdown(f"- {entry}")

        except Exception as e:
            st.error(f"Error: {e}")


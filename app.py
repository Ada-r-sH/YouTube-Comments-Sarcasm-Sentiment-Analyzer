import streamlit as st
import pandas as pd 
from api_youtube import extract_video_id, get_video_details, get_youtube_comments
from ai_analysis import analyze_comment, generate_llm_summary

# ==========================================
# PAGE SETUP
# ==========================================
st.set_page_config(page_title="YouTube Comments Sentiment and Sarcasm analyzer", page_icon="🎬", layout="wide")
st.markdown('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">', unsafe_allow_html=True)

# ==========================================
# FRONTEND UI & DASHBOARD
# ==========================================
st.markdown("<h1><i class='bi bi-youtube' style='color:red;'></i> YouTube Sarcasm & Sentiment Analyzer</h1>", unsafe_allow_html=True)
st.markdown("Enter a YouTube URL below to scrape and analyze the comment section in real-time.")

st.sidebar.markdown("### <i class='bi bi-sliders'></i> Analysis Settings", unsafe_allow_html=True)
weight_likes = st.sidebar.slider(
    "Weight of Likes vs Volume",
    0.0, 1.0, 0.7, 0.05,
    help="Determines the math behind the final score. 100% Volume treats every comment equally. 100% Likes means the score is dictated entirely by the silent majority upvoting specific comments."
)
weight_volume = 1.0 - weight_likes
max_scrape = st.sidebar.number_input("Max Comments to Analyze", min_value=100, max_value=600, value=500, step=100)

video_url = st.text_input("YouTube Video URL:")
analyze_btn = st.button("Run Analysis", type="primary")

if analyze_btn and video_url:
    video_id = extract_video_id(video_url)

    if not video_id:
        st.error("Invalid YouTube URL.")
    else:
        with st.spinner("Fetching Video Metadata..."):
            vid_stats = get_video_details(video_id)

        if vid_stats:
            st.markdown("---")
            col_img, col_info = st.columns([1, 3])
            with col_img:
                st.markdown(f'<img src="{vid_stats["thumbnail"]}" style="width:100%; border-radius:10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
            with col_info:
                st.subheader(vid_stats['title'])
                st.markdown(f"**Channel:** {vid_stats['channel']}")
                v_col1, v_col2, v_col3 = st.columns(3)
                v_col1.metric("Total Views", f"{vid_stats['views']:,}")
                v_col2.metric("Total Likes", f"{vid_stats['likes']:,}")
                v_col3.metric("Total Comments", f"{vid_stats['comments']:,}")
            st.markdown("---")

        status_text = st.empty()
        progress_bar_container = st.empty()

        status_text.info(" Fetching comments from YouTube API...")
        raw_comments = get_youtube_comments(video_id, max_comments=max_scrape)

        if not raw_comments:
            status_text.empty()
            st.warning("No valid comments found.")
        else:
            status_text.info(f" Analyzing {len(raw_comments)} comments with AI Model...")
            positives, negatives, neutrals = [], [], []
            total_pos_likes, total_neg_likes, total_sarcastic = 0, 0, 0

            progress_bar = progress_bar_container.progress(0)
            for idx, item in enumerate(raw_comments):
                ai_result = analyze_comment(item['text'])
                if ai_result['is_sarcastic']: total_sarcastic += 1

                comment_data = {"text": item['text'], "likes": item['likes'], "is_sarcastic": ai_result['is_sarcastic']}
                if ai_result['final_sentiment'] == "Positive":
                    positives.append(comment_data); total_pos_likes += item['likes']
                elif ai_result['final_sentiment'] == "Negative":
                    negatives.append(comment_data); total_neg_likes += item['likes']
                else:
                    neutrals.append(comment_data)
                progress_bar.progress((idx + 1) / len(raw_comments))

            status_text.info(" Generating Summary...")
            llm_summary = generate_llm_summary(positives, negatives, neutrals)
            status_text.empty()
            progress_bar_container.empty()

            total_polar_comments = len(positives) + len(negatives)
            count_pos_pct = (len(positives) / total_polar_comments * 100) if total_polar_comments > 0 else 50.0
            total_likes = total_pos_likes + total_neg_likes
            like_pos_pct = (total_pos_likes / total_likes * 100) if total_likes > 0 else count_pos_pct
            overall_pos_score = (count_pos_pct * weight_volume) + (like_pos_pct * weight_likes)

            st.markdown("### <i class='bi bi-cpu-fill'></i> AI Sentiment Analysis", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            col1.metric("Overall Sentiment", f"{overall_pos_score:.1f}% Positive", help="Calculated by averaging the raw ratio of Positive vs Negative comments against the total volume of 'Likes' on those comments.")
            col2.metric("Total Analyzed", len(positives)+len(negatives)+len(neutrals), help="The exact number of substantive comments evaluated by the AI. This excludes short spam.")
            col3.metric("Sarcasm Detected", total_sarcastic, delta_color="inverse", help="Comments flagged by the secondary neural network for mocking intent. These are forced into the 'Negative' bucket.")

            st.markdown("### <i class='bi bi-robot'></i> Comments Summary", unsafe_allow_html=True, help="Shows the summary generated from the top positive,negative and neutral comments.")
            st.info(llm_summary)

            st.markdown("### <i class='bi bi-search'></i> Deep Dive", unsafe_allow_html=True, help="Shows the top 10 positive,negative and neutral comments classified by the model.")
            tab1, tab2, tab3 = st.tabs(["Positive", "Negative", "Neutral"])

            with tab1:
                for c in sorted(positives, key=lambda x: x['likes'], reverse=True)[:10]:
                    st.markdown(f'<div style="background-color:#d4edda; padding:10px; border-radius:5px; margin-bottom:5px; border-left:5px solid #28a745; color:#155724;"><i class="bi bi-hand-thumbs-up-fill"></i> <b>{c["likes"]} Likes</b><br>{c["text"]}</div>', unsafe_allow_html=True)
            with tab2:
                for c in sorted(negatives, key=lambda x: x['likes'], reverse=True)[:10]:
                    icon = "bi-exclamation-octagon-fill" if c['is_sarcastic'] else "bi-hand-thumbs-down-fill"
                    st.markdown(f'<div style="background-color:#f8d7da; padding:10px; border-radius:5px; margin-bottom:5px; border-left:5px solid #dc3545; color:#721c24;"><i class="bi {icon}"></i> <b>{c["likes"]} Likes</b><br>{c["text"]}</div>', unsafe_allow_html=True)
            with tab3:
                for c in sorted(neutrals, key=lambda x: x['likes'], reverse=True)[:10]:
                    st.markdown(f'<div style="background-color:#fff3cd; padding:10px; border-radius:5px; margin-bottom:5px; border-left:5px solid #ffc107; color:#856404;"><i class="bi bi-chat-dots-fill"></i> <b>{c["likes"]} Likes</b><br>{c["text"]}</div>', unsafe_allow_html=True)
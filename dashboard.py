import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
from dotenv import load_dotenv

# 先に作成した分析モジュールをインポート
from genre_suggestion import suggest_genres
from demand_analysis import analyze_demand
from competition_analysis import analyze_genre_competition
from social_analysis import analyze_genre_social

def run_niche_finder():
    """Streamlitダッシュボードを実行するメイン関数"""
    st.set_page_config(
        page_title="アフィリエイトニッチ発掘ツール",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("アフィリエイトニッチ発掘ダッシュボード 🚀")
    st.markdown("需要が高く競合が少ないアフィリエイトマーケティングのニッチを見つけましょう")
    
    # サイドバーに設定項目を配置
    with st.sidebar:
        st.header("設定")
        
        # APIキーの設定
        st.subheader("APIキー設定")
        
        # 環境変数からデフォルト値を取得
        load_dotenv()
        default_anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
        default_google_key = os.getenv("GOOGLE_API_KEY", "")
        default_twitter_key = os.getenv("TWITTER_BEARER_TOKEN", "")
        
        anthropic_api_key = st.text_input("Anthropic API Key", value=default_anthropic_key, type="password")
        google_api_key = st.text_input("Google API Key", value=default_google_key, type="password")
        twitter_bearer_token = st.text_input("Twitter Bearer Token", value=default_twitter_key, type="password")
        
        st.markdown("---")
        
        # 分析設定
        st.subheader("分析設定")
        num_suggestions = st.slider("提案するジャンル数", min_value=1, max_value=20, value=5)
        
        # 追加の分析設定
        add_tweet_analysis = st.checkbox("Twitter/X分析を実行", value=True)
        
        # 実行ボタン
        start_analysis = st.button("分析開始", type="primary")
    
    # メイン画面のタブ
    tab1, tab2, tab3 = st.tabs(["ジャンル候補", "分析結果", "詳細データ"])
    
    # 状態の初期化（Streamlitのセッション状態）
    if 'genres' not in st.session_state:
        st.session_state.genres = []
    if 'demand_data' not in st.session_state:
        st.session_state.demand_data = {}
    if 'competition_data' not in st.session_state:
        st.session_state.competition_data = {}
    if 'social_data' not in st.session_state:
        st.session_state.social_data = {}
    if 'final_scores' not in st.session_state:
        st.session_state.final_scores = {}
    
    # 分析開始ボタンがクリックされた場合
    if start_analysis:
        with st.spinner("ジャンルを生成中..."):
            if not anthropic_api_key:
                st.error("Anthropic API Keyが設定されていません。")
            else:
                # Claude APIでジャンル提案を取得
                st.session_state.genres = suggest_genres(anthropic_api_key, num_suggestions)
                
                if st.session_state.genres:
                    st.success(f"{len(st.session_state.genres)}個のジャンル候補が生成されました！")
                    
                    # 需要分析
                    with st.spinner("需要分析を実行中..."):
                        st.session_state.demand_data = analyze_demand(st.session_state.genres, google_api_key)
                    
                    # 競合分析
                    with st.spinner("競合分析を実行中..."):
                        st.session_state.competition_data = analyze_genre_competition(st.session_state.genres)
                    
                    # SNS分析（オプション）
                    if add_tweet_analysis:
                        with st.spinner("Twitter/X分析を実行中..."):
                            st.session_state.social_data = analyze_genre_social(st.session_state.genres, twitter_bearer_token)
                    
                    # 総合スコアの計算
                    calculate_final_scores()
                    
                    st.success("分析が完了しました！")
                else:
                    st.error("ジャンル候補の生成に失敗しました。API Keyを確認してください。")
    
    # タブ1の内容: ジャンル候補一覧
    with tab1:
        if st.session_state.genres:
            st.header("提案されたジャンル")
            
            for i, genre in enumerate(st.session_state.genres):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.subheader(f"{i+1}. {genre.get('ジャンル名', 'ジャンル名なし')}")
                    
                    # 総合スコアを表示（分析済みの場合）
                    if genre.get('ジャンル名') in st.session_state.final_scores:
                        score = st.session_state.final_scores[genre.get('ジャンル名')]['総合スコア']
                        st.metric("総合スコア", f"{score:.1f}/100")
                
                with col2:
                    st.markdown(f"**説明**: {genre.get('説明', 'なし')}")
                    st.markdown(f"**ターゲット層**: {genre.get('想定ターゲット層', 'なし')}")
                    
                    # キーワードをチップとして表示
                    keywords = genre.get('関連するキーワード例', [])
                    if keywords:
                        st.markdown("**関連キーワード**:")
                        keyword_html = '<div style="display:flex;flex-wrap:wrap;gap:5px;">'
                        for kw in keywords:
                            keyword_html += f'<div style="background-color:#f0f2f6;padding:5px 10px;border-radius:20px;font-size:0.8em;">{kw}</div>'
                        keyword_html += '</div>'
                        st.markdown(keyword_html, unsafe_allow_html=True)
                
                st.markdown("---")
        else:
            st.info("ジャンル候補はまだ生成されていません。サイドバーで設定を行い、「分析開始」ボタンをクリックしてください。")
    
    # タブ2の内容: 分析結果
    with tab2:
        if st.session_state.final_scores:
            st.header("分析結果")
            
            # 総合スコア順にジャンルをソート
            sorted_genres = sorted(
                st.session_state.final_scores.items(),
                key=lambda x: x[1]['総合スコア'],
                reverse=True
            )
            
            # スコアの表を作成
            scores_df = pd.DataFrame([
                {
                    'ジャンル': genre_name,
                    '総合スコア': data['総合スコア'],
                    '需要スコア': data['需要スコア'],
                    '競合の少なさ': data['競合の少なさスコア'],
                    'SNSスコア': data.get('SNSスコア', 'N/A')
                }
                for genre_name, data in sorted_genres
            ])
            
            # スコア表を表示
            st.dataframe(scores_df, use_container_width=True)
            
            # 棒グラフで総合スコアを表示
            fig_bar = px.bar(
                scores_df,
                x='ジャンル',
                y='総合スコア',
                title='ジャンル別総合スコア',
                color='総合スコア',
                color_continuous_scale='Viridis',
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # レーダーチャートで詳細スコアを表示
            cols = st.columns(2)
            
            for i, (genre_name, data) in enumerate(sorted_genres[:4]):  # 上位4つのみ表示
                if i % 2 == 0:
                    current_col = cols[0]
                else:
                    current_col = cols[1]
                
                with current_col:
                    categories = ['需要スコア', '競合の少なさ', 'SNSスコア']
                    values = [
                        data['需要スコア'],
                        data['競合の少なさスコア'],
                        data.get('SNSスコア', 0)
                    ]
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill='toself',
                        name=genre_name
                    ))
                    
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 100]
                            )
                        ),
                        showlegend=False,
                        title=genre_name
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("分析結果はまだありません。サイドバーで設定を行い、「分析開始」ボタンをクリックしてください。")
    
    # タブ3の内容: 詳細データ
    with tab3:
        if st.session_state.demand_data and st.session_state.competition_data:
            st.header("詳細データ")
            
            # ジャンル選択
            genre_names = list(st.session_state.demand_data.keys())
            if genre_names:
                selected_genre = st.selectbox("ジャンルを選択", genre_names)
                
                if selected_genre:
                    st.subheader(f"{selected_genre}の詳細データ")
                    
                    # 需要データ
                    st.markdown("### 需要分析")
                    demand_data = st.session_state.demand_data.get(selected_genre, {})
                    
                    # キーワードごとのデータを表示
                    if 'キーワード分析' in demand_data:
                        keyword_data = []
                        for kw, data in demand_data['キーワード分析'].items():
                            keyword_data.append({
                                'キーワード': kw,
                                '平均関心度': data.get('トレンド情報', {}).get('平均関心度', 0),
                                'トレンド': data.get('トレンド情報', {}).get('トレンド', '不明'),
                                '月間検索ボリューム': data.get('月間検索ボリューム', 0)
                            })
                        
                        if keyword_data:
                            kw_df = pd.DataFrame(keyword_data)
                            st.dataframe(kw_df, use_container_width=True)
                            
                            # 検索ボリュームのグラフ
                            fig = px.bar(
                                kw_df,
                                x='キーワード',
                                y='月間検索ボリューム',
                                title='キーワード別検索ボリューム',
                                color='トレンド'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    
                    # 競合データ
                    st.markdown("### 競合分析")
                    competition_data = st.session_state.competition_data.get(selected_genre, {})
                    
                    if 'キーワード競合分析' in competition_data:
                        comp_data = []
                        for kw, data in competition_data['キーワード競合分析'].items():
                            comp_data.append({
                                'キーワード': kw,
                                '難易度': data.get('キーワード難易度', 0),
                                '競合サイト数': data.get('競合サイト数', 0),
                                'データソース': data.get('データソース', '不明')
                            })
                        
                        if comp_data:
                            comp_df = pd.DataFrame(comp_data)
                            st.dataframe(comp_df, use_container_width=True)
                            
                            # 難易度のグラフ
                            fig = px.scatter(
                                comp_df,
                                x='難易度',
                                y='競合サイト数',
                                size='競合サイト数',
                                color='キーワード',
                                title='キーワード別競合状況',
                                log_y=True
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    
                    # SNSデータ（存在する場合）
                    if selected_genre in st.session_state.social_data:
                        st.markdown("### SNS分析")
                        social_data = st.session_state.social_data.get(selected_genre, {})
                        
                        if 'SNS分析' in social_data:
                            social_data_list = []
                            for kw, data in social_data['SNS分析'].items():
                                social_data_list.append({
                                    'キーワード': kw,
                                    'ツイート数': data.get('総ツイート数', 0),
                                    'エンゲージメント率': data.get('平均エンゲージメント率', 0),
                                    '感情傾向': data.get('感情傾向', '中立')
                                })
                            
                            if social_data_list:
                                social_df = pd.DataFrame(social_data_list)
                                st.dataframe(social_df, use_container_width=True)
                                
                                # ツイート数とエンゲージメントのグラフ
                                fig = px.scatter(
                                    social_df,
                                    x='ツイート数',
                                    y='エンゲージメント率',
                                    size='ツイート数',
                                    color='感情傾向',
                                    hover_name='キーワード',
                                    title='Twitter/X エンゲージメント分析'
                                )
                                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ジャンルデータがありません。")
        else:
            st.info("詳細データはまだ生成されていません。サイドバーで設定を行い、「分析開始」ボタンをクリックしてください。")

def calculate_final_scores():
    """総合スコアを計算する関数"""
    final_scores = {}
    
    for genre_name in st.session_state.demand_data.keys():
        # 各スコアを取得
        demand_score = st.session_state.demand_data.get(genre_name, {}).get('需要スコア', 0)
        competition_score = st.session_state.competition_data.get(genre_name, {}).get('競合の少なさスコア', 0)
        social_score = st.session_state.social_data.get(genre_name, {}).get('SNSスコア', 0) if genre_name in st.session_state.social_data else 0
        
        # 重み付けした総合スコアを計算
        # 需要: 40%, 競合: 40%, SNS: 20%
        if genre_name in st.session_state.social_data:
            total_score = (demand_score * 0.4) + (competition_score * 0.4) + (social_score * 0.2)
        else:
            # SNSデータがない場合は需要と競合のみで計算
            total_score = (demand_score * 0.5) + (competition_score * 0.5)
        
        final_scores[genre_name] = {
            '総合スコア': total_score,
            '需要スコア': demand_score,
            '競合の少なさスコア': competition_score
        }
        
        if genre_name in st.session_state.social_data:
            final_scores[genre_name]['SNSスコア'] = social_score
    
    st.session_state.final_scores = final_scores

if __name__ == "__main__":
    run_niche_finder()
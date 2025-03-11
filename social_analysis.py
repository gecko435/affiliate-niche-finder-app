import requests
import json
import time
import os
from dotenv import load_dotenv
import pandas as pd

def analyze_twitter_engagement(keywords, twitter_bearer_token=None):
    """
    Twitter/X APIを使用してキーワードに関連するツイートのエンゲージメントを分析
    
    Parameters:
    keywords (list): 分析するキーワードのリスト
    twitter_bearer_token (str): Twitter API Bearer Token
    
    Returns:
    dict: キーワードごとのエンゲージメント分析結果
    """
    results = {}
    
    for keyword in keywords:
        try:
            if twitter_bearer_token:
                data = get_twitter_data(keyword, twitter_bearer_token)
                results[keyword] = {
                    "総ツイート数": data.get("総ツイート数", 0),
                    "平均エンゲージメント率": data.get("平均エンゲージメント率", 0),
                    "感情傾向": data.get("感情傾向", "中立"),
                    "データソース": "Twitter API"
                }
            else:
                results[keyword] = mock_twitter_data(keyword)
            
            # APIレート制限を考慮
            time.sleep(1)
            
        except Exception as e:
            print(f"Twitter分析エラー ({keyword}): {e}")
            results[keyword] = mock_twitter_data(keyword)
    
    return results

def get_twitter_data(keyword, bearer_token):
    """
    Twitter APIからキーワードに関連するツイートデータを取得
    （注: 実際の実装ではTwitterの公式APIドキュメントに従って実装する必要があります）
    
    2023年以降のX/Twitter APIはv2を使用します
    """
    # 実際のTwitter API v2実装例
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }
    
    # 検索クエリパラメータ
    query = f"{keyword} lang:ja -is:retweet"
    params = {
        "query": query,
        "max_results": 100,
        "tweet.fields": "public_metrics,created_at"
    }
    
    # Twitter API v2エンドポイント
    # url = "https://api.twitter.com/2/tweets/search/recent"
    # response = requests.get(url, headers=headers, params=params)
    
    # ここでレスポンスをパースしてエンゲージメントを計算する
    
    # モックデータを返す（実際の実装では削除）
    return mock_twitter_data(keyword)

def mock_twitter_data(keyword):
    """モックTwitterデータ生成（APIが利用できない場合のテスト用）"""
    import random
    import hashlib
    
    # キーワードからハッシュ値を生成し、それを整数に変換して一貫性のあるランダム値を生成
    hash_obj = hashlib.md5(keyword.encode())
    hash_int = int(hash_obj.hexdigest(), 16)
    random.seed(hash_int)
    
    # キーワードの特性に基づいてツイート数を調整
    base_tweets = random.randint(50, 5000)
    
    # 一般的な話題はツイート数が多いと仮定
    common_topics = ["食べ物", "旅行", "アニメ", "ゲーム", "健康", "スポーツ"]
    topic_factor = any(topic in keyword for topic in common_topics)
    tweet_count = base_tweets * (3 if topic_factor else 1)
    
    # エンゲージメント率の計算（いいね、リツイート、返信の合計÷ツイート数）
    engagement_rate = random.uniform(0.5, 10.0)
    
    # 感情傾向
    sentiment_options = ["ポジティブ", "やや肯定的", "中立", "やや否定的", "ネガティブ"]
    sentiment_weights = [0.2, 0.3, 0.3, 0.15, 0.05]  # 多くのツイートは中立か肯定的
    sentiment = random.choices(sentiment_options, weights=sentiment_weights, k=1)[0]
    
    return {
        "総ツイート数": tweet_count,
        "平均エンゲージメント率": round(engagement_rate, 2),
        "感情傾向": sentiment,
        "データソース": "モックデータ"
    }

def analyze_genre_social(genres, twitter_bearer_token=None):
    """
    提案されたジャンルのSNS上での反応を分析する
    
    Parameters:
    genres (list or dict or str): ジャンル情報
    twitter_bearer_token (str): Twitter API Bearer Token（オプション）
    
    Returns:
    dict: ジャンルごとのSNS分析結果
    """
    all_results = {}
    
    # genresがリストでなければ、変換を試みる
    if not isinstance(genres, list):
        try:
            # 文字列の場合、JSONとしてパースを試みる
            if isinstance(genres, str):
                print("文字列をJSONに変換しています...")
                genres = json.loads(genres)
            
            # 辞書の場合、特定のキーにジャンルリストがあるか確認
            if isinstance(genres, dict):
                for key in ["genres", "ジャンル", "results", "data"]:
                    if key in genres and isinstance(genres[key], list):
                        genres = genres[key]
                        break
                # キーが見つからなければ、単一のジャンル情報として扱う
                if isinstance(genres, dict):
                    genres = [genres]
        except Exception as e:
            print(f"ジャンルデータの変換エラー: {e}")
            return {}
    
    # 変換後もジャンルリストが整数、浮動小数点、文字列の場合はエラー
    if isinstance(genres, (int, float, str)):
        print(f"ジャンルデータの形式が不正です: {type(genres)}")
        print(f"データの内容: {genres}")
        return {}
    
    # ここでジャンル情報をループ処理
    for genre in genres:
        # genreが辞書でなければスキップ
        if not isinstance(genre, dict):
            if isinstance(genre, str):
                # 単純な文字列の場合、ジャンル名として扱う
                genre_name = genre
                keywords = [genre]  # キーワードとしても使用
            else:
                print(f"不正なジャンル形式をスキップ: {type(genre)}")
                continue
        else:
            # 通常の辞書形式処理
            genre_name = genre.get("ジャンル名", "")
            keywords = genre.get("関連するキーワード例", [])
        
        if not genre_name:
            continue
            
        if not keywords:
            continue
            
        # Twitter/X分析を実行
        twitter_data = analyze_twitter_engagement(keywords, twitter_bearer_token)
        
        # 結果をまとめる
        genre_result = {
            "ジャンル名": genre_name,
            "SNS分析": twitter_data
        }
        
        # ジャンル全体のSNSスコア計算
        avg_tweet_count = sum([data.get("総ツイート数", 0) for data in twitter_data.values()]) / len(twitter_data) if twitter_data else 0
        avg_engagement = sum([data.get("平均エンゲージメント率", 0) for data in twitter_data.values()]) / len(twitter_data) if twitter_data else 0
        
        # 感情傾向をスコア化（ポジティブ: 1.0, やや肯定的: 0.5, 中立: 0, やや否定的: -0.5, ネガティブ: -1.0）
        sentiment_map = {
            "ポジティブ": 1.0,
            "やや肯定的": 0.5,
            "中立": 0.0,
            "やや否定的": -0.5,
            "ネガティブ": -1.0
        }
        
        avg_sentiment = sum([sentiment_map.get(data.get("感情傾向", "中立"), 0) for data in twitter_data.values()]) / len(twitter_data) if twitter_data else 0
        
        # 正規化（0-100）したスコア
        tweet_count_score = min(100, avg_tweet_count / 50)  # 5000ツイートで100点
        engagement_score = min(100, avg_engagement * 10)    # エンゲージメント率10%で100点
        sentiment_score = (avg_sentiment + 1) * 50          # -1から1の範囲を0-100に変換
        
        # 総合SNSスコア（ツイート数、エンゲージメント率、感情傾向の加重平均）
        genre_result["SNSスコア"] = (tweet_count_score * 0.3) + (engagement_score * 0.5) + (sentiment_score * 0.2)
        
        all_results[genre_name] = genre_result
    
    return all_results
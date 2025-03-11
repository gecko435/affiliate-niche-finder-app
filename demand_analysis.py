from pytrends.request import TrendReq
import pandas as pd
import time
from googleapiclient.discovery import build
import json

def analyze_trends(keywords, timeframe='today 12-m', geo='JP'):
    """
    Google Trendsを使用してキーワードの検索トレンドを分析する
    
    Parameters:
    keywords (list): 分析するキーワードのリスト
    timeframe (str): 分析する期間（例：'today 12-m'は過去12ヶ月）
    geo (str): 地域コード（日本は'JP'）
    
    Returns:
    dict: キーワードごとの平均関心度とトレンド（上昇/下降）
    """
    result = {}
    pytrends = TrendReq(hl='ja-JP', tz=540)  # 日本のタイムゾーン (UTC+9)
    
    # キーワードを5つずつグループ化（Google Trendsの制限）
    keyword_groups = [keywords[i:i+5] for i in range(0, len(keywords), 5)]
    
    for group in keyword_groups:
        try:
            pytrends.build_payload(group, cat=0, timeframe=timeframe, geo=geo)
            interest_over_time = pytrends.interest_over_time()
            
            if not interest_over_time.empty:
                for keyword in group:
                    if keyword in interest_over_time.columns:
                        values = interest_over_time[keyword].values
                        avg_interest = values.mean()
                        
                        # トレンド判定（単純な線形回帰で上昇/下降を判断）
                        if len(values) > 1:
                            first_half = values[:len(values)//2].mean()
                            second_half = values[len(values)//2:].mean()
                            trend = "上昇" if second_half > first_half else "下降"
                        else:
                            trend = "不明"
                        
                        result[keyword] = {
                            "平均関心度": float(avg_interest),
                            "トレンド": trend
                        }
            
            # Google Trendsのレート制限を避けるための待機
            time.sleep(1)
            
        except Exception as e:
            print(f"Google Trendsエラー: {e}")
    
    return result

def get_search_volume(keywords, api_key):
    """
    Google Ads APIを使用してキーワードの検索ボリュームを取得する
    
    Parameters:
    keywords (list): 分析するキーワードのリスト
    api_key (str): Google Developer API Key
    
    Returns:
    dict: キーワードごとの月間検索ボリューム
    """
    # 注意: 実際のGoogle Ads APIの使用には、OAuth認証と正式なGoogle Adsアカウントが必要です
    # このコードは簡略化されたもので、実際の実装では適切な認証が必要です
    
    # 模擬的なデータを返す関数（実際の実装ではGoogle Ads APIを呼び出す）
    def mock_search_volume(keyword):
        import random
        # 実際の実装では、この部分をGoogle Ads APIの呼び出しに置き換える
        return random.randint(500, 10000)
    
    result = {}
    for keyword in keywords:
        try:
            # 実際はここでGoogle Ads APIを呼び出す
            volume = mock_search_volume(keyword)
            result[keyword] = volume
            time.sleep(0.5)  # APIレート制限を考慮
        except Exception as e:
            print(f"検索ボリューム取得エラー: {e}")
    
    return result

def analyze_demand(genres, google_api_key):
    """
    提案されたジャンルの需要を分析する
    
    Parameters:
    genres (list or dict or str): ジャンル情報
    google_api_key (str): Google API Key
    
    Returns:
    dict: ジャンルごとの需要分析結果
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
            
        # Google Trendsで分析
        trends_data = analyze_trends(keywords)
        
        # 検索ボリュームを取得
        search_volume = get_search_volume(keywords, google_api_key)
        
        # 結果を結合
        genre_result = {
            "ジャンル名": genre_name,
            "キーワード分析": {}
        }
        
        for keyword in keywords:
            keyword_result = {
                "トレンド情報": trends_data.get(keyword, {"平均関心度": 0, "トレンド": "不明"}),
                "月間検索ボリューム": search_volume.get(keyword, 0)
            }
            genre_result["キーワード分析"][keyword] = keyword_result
        
        # ジャンル全体のスコア計算（単純な平均）
        avg_interest = sum([trends_data.get(k, {}).get("平均関心度", 0) for k in keywords]) / len(keywords) if keywords else 0
        avg_volume = sum([search_volume.get(k, 0) for k in keywords]) / len(keywords) if keywords else 0
        trend_score = len([k for k in keywords if trends_data.get(k, {}).get("トレンド", "") == "上昇"]) / len(keywords) if keywords else 0
        
        genre_result["需要スコア"] = (avg_interest * 0.3) + (avg_volume * 0.5) + (trend_score * 100 * 0.2)
        
        all_results[genre_name] = genre_result
    
    return all_results
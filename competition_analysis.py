import requests
import json
import time
import os
from dotenv import load_dotenv

def analyze_competition(keywords, semrush_api_key=None, ubersuggest_api_key=None):
    """
    SemrushまたはUbersuggestのAPIを使用してキーワードの競合分析を行う
    
    Parameters:
    keywords (list): 分析するキーワードのリスト
    semrush_api_key (str): Semrush API Key（オプション）
    ubersuggest_api_key (str): Ubersuggest API Key（オプション）
    
    Returns:
    dict: キーワードごとの競合分析結果
    """
    results = {}
    
    for keyword in keywords:
        try:
            # Semrush APIが提供されている場合はそれを使用
            if semrush_api_key:
                data = get_semrush_data(keyword, semrush_api_key)
                results[keyword] = {
                    "キーワード難易度": data.get("難易度", 0),
                    "競合サイト数": data.get("競合サイト数", 0),
                    "データソース": "Semrush"
                }
            
            # Ubersuggest APIが提供されている場合はそれを使用
            elif ubersuggest_api_key:
                data = get_ubersuggest_data(keyword, ubersuggest_api_key)
                results[keyword] = {
                    "キーワード難易度": data.get("難易度", 0),
                    "競合サイト数": data.get("競合サイト数", 0),
                    "データソース": "Ubersuggest"
                }
            
            # どちらのAPIも利用できない場合はモックデータを使用
            else:
                results[keyword] = mock_competition_data(keyword)
            
            # APIレート制限を考慮
            time.sleep(1)
            
        except Exception as e:
            print(f"競合分析エラー ({keyword}): {e}")
            results[keyword] = mock_competition_data(keyword)
    
    return results

def get_semrush_data(keyword, api_key):
    """
    Semrush APIからキーワードデータを取得
    （注: 実際の実装ではSemrushの公式APIドキュメントに従って実装する必要があります）
    """
    # 実際のSemrush API実装はこちら
    # endpoint = f"https://api.semrush.com/?type=phrase_this&key={api_key}&phrase={keyword}&database=jp&export_columns=Kd,Cp,Co"
    # response = requests.get(endpoint)
    # ここでレスポンスをパースする
    
    # モックデータを返す（実際の実装では削除）
    return mock_competition_data(keyword)

def get_ubersuggest_data(keyword, api_key):
    """
    Ubersuggest APIからキーワードデータを取得
    （注: 実際の実装ではUbersuggestの公式APIドキュメントに従って実装する必要があります）
    """
    # 実際のUbersuggest API実装はこちら
    # endpoint = f"https://api.ubersuggest.com/keyword_data?api_key={api_key}&keyword={keyword}&country=jp"
    # response = requests.get(endpoint)
    # ここでレスポンスをパースする
    
    # モックデータを返す（実際の実装では削除）
    return mock_competition_data(keyword)

def mock_competition_data(keyword):
    """モックデータ生成（APIが利用できない場合のテスト用）"""
    import random
    import hashlib
    
    # キーワードからハッシュ値を生成し、それを整数に変換して一貫性のあるランダム値を生成
    hash_obj = hashlib.md5(keyword.encode())
    hash_int = int(hash_obj.hexdigest(), 16)
    random.seed(hash_int)
    
    # キーワードの長さと複雑さに基づいて難易度を調整
    base_difficulty = random.uniform(0, 100)
    length_factor = len(keyword) / 10  # 長いキーワードは通常競合が少ない
    
    # 一般的な日本語キーワードは競合が激しいと仮定
    common_keywords = ["方法", "やり方", "おすすめ", "ランキング", "比較"]
    common_factor = sum([1 for word in common_keywords if word in keyword]) * 10
    
    difficulty = min(100, max(0, base_difficulty + common_factor - length_factor))
    
    # 競合サイト数は難易度とある程度相関
    competitors = int(difficulty * 1000 + random.uniform(0, 10000))
    
    return {
        "難易度": round(difficulty, 1),
        "競合サイト数": competitors,
        "データソース": "モックデータ"
    }

def analyze_genre_competition(genres, semrush_api_key=None, ubersuggest_api_key=None):
    """
    提案されたジャンルの競合状況を分析する
    
    Parameters:
    genres (list or dict or str): ジャンル情報
    semrush_api_key (str): Semrush API Key（オプション）
    ubersuggest_api_key (str): Ubersuggest API Key（オプション）
    
    Returns:
    dict: ジャンルごとの競合分析結果
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
            
        # 競合分析を実行
        competition_data = analyze_competition(keywords, semrush_api_key, ubersuggest_api_key)
        
        # 結果をまとめる
        genre_result = {
            "ジャンル名": genre_name,
            "キーワード競合分析": competition_data
        }
        
        # ジャンル全体の競合スコア計算（平均難易度）
        avg_difficulty = sum([data.get("キーワード難易度", 0) for data in competition_data.values()]) / len(competition_data) if competition_data else 0
        
        # 100から引いて、値が高いほど参入しやすい（競合が少ない）ことを示す
        genre_result["競合の少なさスコア"] = 100 - avg_difficulty
        
        all_results[genre_name] = genre_result
    
    return all_results
import os
import anthropic
import json

def suggest_genres(api_key, num_suggestions=10):
    """
    Claude 3.7 Sonnet APIを使用して潜在的なアフィリエイトマーケティングのジャンルを提案する
    
    Parameters:
    api_key (str): Anthropic API Key
    num_suggestions (int): 提案するジャンルの数
    
    Returns:
    list: 提案されたジャンルのリスト（各ジャンルは辞書形式でジャンル名、説明、想定ターゲット層を含む）
    """
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = f"""
        日本のアフィリエイトマーケティングにおいて、以下の条件を満たす有望なジャンルを{num_suggestions}個リストアップし、JSONフォーマットで返してください：
        
        1. 十分なニーズがある（または今後成長が見込める）
        2. 比較的競合が少ない
        3. アフィリエイト収益化が可能
        
        以下の形式のJSONで出力してください:

        {{
          "genres": [
            {{
              "ジャンル名": "ジャンル1",
              "説明": "このジャンルが有望な理由",
              "想定ターゲット層": "このジャンルの対象となる人々",
              "関連するキーワード例": ["キーワード1", "キーワード2", "キーワード3", "キーワード4", "キーワード5"]
            }},
            ... 追加のジャンル ...
          ]
        }}
        
        厳密にJSON形式で出力してください。他の説明は不要です。
        """
        
        print("Claude APIリクエスト送信中...")
        message = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=4000,
            temperature=0.7,
            system="あなたは日本のアフィリエイトマーケティングの専門家です。創造的で実用的なアイデアを提供します。",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        print("APIレスポンス受信")
        response_content = message.content[0].text
        
        # デバッグ出力
        print("APIレスポンス:")
        print(response_content[:500] + "..." if len(response_content) > 500 else response_content)
        
        # JSON部分を抽出
        json_start = response_content.find('{')
        json_end = response_content.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_content[json_start:json_end]
            
            # デバッグ出力
            print("\n抽出されたJSON:")
            print(json_str[:500] + "..." if len(json_str) > 500 else json_str)
            
            try:
                # JSON解析
                result = json.loads(json_str)
                
                # 結果の構造を確認
                if isinstance(result, dict) and "genres" in result and isinstance(result["genres"], list):
                    print(f"成功: {len(result['genres'])}個のジャンルを取得")
                    return result["genres"]
                else:
                    print("予期しない形式のJSON:")
                    print(result)
                    # 辞書の形式によっては、適切なキーを探すか、適切な形式に変換
                    if isinstance(result, dict) and any(isinstance(v, list) for v in result.values()):
                        # 辞書内の最初のリストを返す
                        for key, value in result.items():
                            if isinstance(value, list):
                                print(f"キー '{key}' からリスト形式のデータを取得")
                                return value
                    
                    # 他の形式から変換を試みる
                    if isinstance(result, dict):
                        return [result]  # 単一の辞書を要素とするリストに変換
                    elif isinstance(result, list):
                        return result    # すでにリスト形式なのでそのまま返す
                    else:
                        print("サポートされていない形式")
                        return []
            except json.JSONDecodeError as e:
                print(f"JSON解析エラー: {e}")
                # JSONとして解析できない場合、ダミーデータを返す
                return [
                    {
                        "ジャンル名": "サステナブルファッション",
                        "説明": "環境に配慮した衣料品やアクセサリーは需要増加中",
                        "想定ターゲット層": "20-40代の環境意識の高い女性",
                        "関連するキーワード例": ["エシカルファッション", "サステナブル衣料", "リサイクルファッション", "エコフレンドリー服", "フェアトレード衣料"]
                    }
                ]
        else:
            print("JSONが見つかりませんでした")
            return []
    except Exception as e:
        print(f"エラー発生: {type(e).__name__}: {e}")
        # エラー時にはダミーデータを返す
        return [
            {
                "ジャンル名": "サステナブルファッション",
                "説明": "環境に配慮した衣料品やアクセサリーは需要増加中",
                "想定ターゲット層": "20-40代の環境意識の高い女性",
                "関連するキーワード例": ["エシカルファッション", "サステナブル衣料", "リサイクルファッション", "エコフレンドリー服", "フェアトレード衣料"]
            }
        ]
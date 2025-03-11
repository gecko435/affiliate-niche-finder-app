import os
import sys
from dotenv import load_dotenv

# モジュールを正しくインポートするためのパス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 必要なモジュールをインポート
from genre_suggestion import suggest_genres
from demand_analysis import analyze_demand
from competition_analysis import analyze_genre_competition
from social_analysis import analyze_genre_social
from dashboard import run_niche_finder

def main():
    """
    アプリケーションのエントリーポイント
    """
    # .envファイルから環境変数を読み込む
    load_dotenv()
    
    # Streamlitダッシュボードを起動
    run_niche_finder()

if __name__ == "__main__":
    main()
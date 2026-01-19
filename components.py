"""
このファイルは、画面表示に特化した関数定義のファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
import logging
import streamlit as st
import constants as ct


############################################################
# 関数定義
############################################################

def display_app_title():
    """
    タイトル表示
    """
    st.markdown(f"## {ct.APP_NAME}")


def display_initial_ai_message():
    """
    AIメッセージの初期表示
    """
    with st.chat_message("assistant", avatar=ct.AI_ICON_FILE_PATH):
        st.markdown("こちらは対話型の商品レコメンド生成AIアプリです。「こんな商品が欲しい」という情報・要望を画面下部のチャット欄から送信いただければ、おすすめの商品をレコメンドいたします。")
        st.markdown("**入力例**")
        st.info("""
        - 「長時間使える、高音質なワイヤレスイヤホン」
        - 「机のライト」
        - 「USBで充電できる加湿器」
        """)


def display_conversation_log():
    """
    会話ログの一覧表示
    """
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user", avatar=ct.USER_ICON_FILE_PATH):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar=ct.AI_ICON_FILE_PATH):
                display_product(message["content"])


def display_product(result):
    """
    商品情報の表示

    Args:
        result: LLMからの回答
    """
    logger = logging.getLogger(ct.LOGGER_NAME)

    # LLMレスポンスのテキストを辞書に変換
    try:
        # resultがDocumentオブジェクトのリストの場合
        if hasattr(result[0], 'page_content'):
            content = result[0].page_content
        else:
            # resultが文字列のリストの場合
            content = result[0] if isinstance(result[0], str) else str(result[0])
        
        # BOM（Byte Order Mark）を除去
        if content.startswith('\ufeff'):
            content = content[1:]
        
        product_lines = content.split("\n")
        product = {}
        
        for item in product_lines:
            item = item.strip()
            # 空行をスキップ
            if not item:
                continue
            # ": "で分割できるかチェック
            if ": " in item:
                parts = item.split(": ", 1)  # 最大1回だけ分割（値に": "が含まれる場合に対応）
                if len(parts) == 2:
                    key = parts[0].strip()
                    # キーからBOMやその他の不可視文字を除去
                    key = key.lstrip('\ufeff').strip()
                    value = parts[1].strip()
                    product[key] = value
        
        # デバッグ用ログ
        logger.debug(f"Parsed product: {product}")
        
        # 必要なキーが存在するかチェック
        required_keys = ['name', 'id', 'price', 'category', 'maker', 'score', 'review_number', 'file_name', 'description', 'recommended_people', 'stock_status']
        missing_keys = [key for key in required_keys if key not in product]
        if missing_keys:
            logger.error(f"Missing required keys: {missing_keys}")
            logger.error(f"Product content: {content}")
            raise KeyError(f"Missing required keys: {missing_keys}")
            
    except (IndexError, AttributeError, KeyError) as e:
        logger.error(f"Error parsing product data: {e}")
        logger.error(f"Result type: {type(result)}, Result content: {result}")
        raise

    st.markdown("以下の商品をご提案いたします。")

    # 「商品名」と「価格」
    st.success(f"""
            商品名：{product['name']}（商品ID: {product['id']}）\n
            価格：{product['price']}
    """)

    # 提出課題 【手順２】
    if product['stock_status'] == ct.STOCK_STATUS_WARNING:
        st.warning(f"⚠️ {ct.STOCK_STATUS_WARNING_MESSAGE}")
    elif product['stock_status'] == ct.STOCK_STATUS_OUT_OF_STOCK:
        st.error(f"❗️ {ct.STOCK_STATUS_OUT_OF_STOCK_MESSAGE}")
    
    # 「商品カテゴリ」と「メーカー」と「ユーザー評価」
    st.code(f"""
        商品カテゴリ：{product['category']}\n
        メーカー：{product['maker']}\n
        評価：{product['score']}({product['review_number']}件)
    """, language=None, wrap_lines=True)

    # 商品画像
    st.image(f"images/products/{product['file_name']}", width=400)

    # 商品説明
    st.code(product['description'], language=None, wrap_lines=True)

    # おすすめ対象ユーザー
    st.markdown("**こんな方におすすめ！**")
    st.info(product["recommended_people"])

    # 商品ページのリンク
    st.link_button("商品ページを開く", type="primary", use_container_width=True, url="https://google.com")
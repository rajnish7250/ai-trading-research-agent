from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ---------------------------------------------------
# STEP 1 — Create Large Research Documents
# ---------------------------------------------------
documents = [

    Document(
        page_content="""
Bitcoin surged sharply after ETF approval from regulators.

Institutional investors increased exposure aggressively.

Trading volume expanded significantly across major exchanges.

Ethereum underperformed against Bitcoin during the same period.

Federal Reserve uncertainty continued affecting global liquidity conditions.

Risk appetite improved across crypto markets after inflation cooled.
""",

        metadata={
            "ticker": "BTC",
            "source": "news_agent",
            "date": "2026-05-20",
            "market": "crypto"
        }
    ),

    Document(
        page_content="""
Gold prices remained stable despite volatility in equity markets.

Investors moved toward safe-haven assets after macroeconomic uncertainty increased.

Central bank policy decisions continued influencing commodity prices.

US dollar weakness supported precious metals demand globally.
""",

        metadata={
            "ticker": "GOLD",
            "source": "macro_agent",
            "date": "2026-05-20",
            "market": "commodities"
        }
    )
]


#Create text splitter
text_splitter = RecursiveCharacterTextSplitter(

    # Maximum size of each chunk
    chunk_size=500,    

    # Shared text between chunks
    chunk_overlap=100,

    # Helps preserve sentence/paragraph structure
    separators=[
        "\n\n", #Paragraph
        "\n",#line
        ". ",#sentence
        " ",#word
        ""#character
    ]
)

#Split Documents into chunks
split_docs =text_splitter.split_documents(documents)

def get_split_documents():
    return split_docs

if __name__=="__main__":
    
    
    #Print chunks
    print(f"\n Total Chunks Created: {len(split_docs)}")
    
    for i, doc in enumerate(split_docs):
        
        print("\n" + "="*50)
        print(f"CHUNK {i+1}")
        print("="*50)
        
        print("\nCONTENT:\n")
        print(doc.page_content)
        
        print("\nMETADATA\n")
        print(doc.metadata)

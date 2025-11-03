"""
Streamlit chat interface for the liquor store AI assistant.
Provides a user-friendly web interface for natural language queries.
"""

import streamlit as st
from config.settings import GEMINI_API_KEY
from llm.gemini import GeminiLLM
from llm.tools import GEMINI_TOOLS, SYSTEM_PROMPT

# Page configuration
st.set_page_config(
    page_title="LiSearch - Liquor Store AI Assistant",
    page_icon="🍷",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
    
if 'llm' not in st.session_state:
    st.session_state.llm = GeminiLLM(
        api_key=GEMINI_API_KEY,
        model_name="gemini-2.5-flash-lite"
    )

if 'show_debug' not in st.session_state:
    st.session_state.show_debug = False


# Sidebar
with st.sidebar:
    st.title("🍷 LiSearch")
    st.markdown("### Liquor Store AI Assistant")
    st.markdown("---")
    
    st.markdown("**Ask me about:**")
    st.markdown("- 📈 Top selling products")
    st.markdown("- 🔥 Trending items")
    st.markdown("- 🔍 Product search")
    st.markdown("- 📦 Inventory status")
    st.markdown("- 📊 Sales analytics")
    
    st.markdown("---")
    
    # Debug mode toggle
    st.session_state.show_debug = st.checkbox(
        "Show debug info",
        value=st.session_state.show_debug,
        help="Display tool calls and iterations"
    )
    
    # Clear conversation button
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("**Example queries:**")
    examples = [
        "What are the top 5 selling wines?",
        "Show me trending beers this week",
        "What products are low in stock?",
        "Search for citrus flavor drinks",
        "Sales summary by category"
    ]
    
    for example in examples:
        if st.button(f"💡 {example}", use_container_width=True, key=example):
            # Add example to input
            st.session_state.example_query = example


# Main chat interface
st.title("💬 Chat with Your Store Data")
st.markdown("Ask natural language questions about your inventory and sales!")

# Display chat messages
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    
    with st.chat_message(role):
        st.markdown(content)
        
        # Show debug info if enabled
        if st.session_state.show_debug and "debug_info" in message:
            debug = message["debug_info"]
            with st.expander("🔧 Debug Info"):
                st.json({
                    "iterations": debug.get("iterations", 0),
                    "tools_used": [
                        {
                            "name": tc["name"],
                            "args": tc["arguments"]
                        }
                        for tc in debug.get("tool_calls_made", [])
                    ]
                })

# Chat input
user_input = st.chat_input("Ask about your store data...")

# Handle example query from sidebar
if 'example_query' in st.session_state:
    user_input = st.session_state.example_query
    del st.session_state.example_query

# Process user input
if user_input:
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Prepare conversation history
                conversation_history = [
                    {"role": "system", "content": SYSTEM_PROMPT}
                ]
                
                # Add previous messages (limit to last 10 for context)
                for msg in st.session_state.messages[-10:]:
                    if msg["role"] in ["user", "assistant"]:
                        conversation_history.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
                
                # Get response with tool calling
                result = st.session_state.llm.chat_with_tools(
                    user_message=user_input,
                    conversation_history=conversation_history[:-1],  # Exclude the user message we just added
                    tools=GEMINI_TOOLS,
                    max_iterations=5
                )
                
                response_text = result.get('response', 'I apologize, but I could not generate a response.')
                
                # Display response
                st.markdown(response_text)
                
                # Show debug info if enabled
                if st.session_state.show_debug:
                    with st.expander("🔧 Debug Info"):
                        st.json({
                            "iterations": result.get("iterations", 0),
                            "tools_used": [
                                {
                                    "name": tc["name"],
                                    "args": tc["arguments"]
                                }
                                for tc in result.get("tool_calls_made", [])
                            ]
                        })
                
                # Add assistant message to chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "debug_info": {
                        "iterations": result.get("iterations", 0),
                        "tool_calls_made": result.get("tool_calls_made", [])
                    }
                })
                
            except Exception as e:
                error_message = f"❌ Error: {str(e)}"
                st.error(error_message)
                
                # Add error to conversation
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message
                })

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Built with Streamlit, Gemini AI, and Supabase | "
    "<a href='https://github.com/yourusername/lisearch' target='_blank'>GitHub</a>"
    "</div>",
    unsafe_allow_html=True
)
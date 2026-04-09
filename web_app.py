import streamlit as st
import asyncio
import os
from config import GEMINI_API_KEY, OLLAMA_MODELS, GEMINI_MODEL
from models.gemini import GeminiModel
from models.ollama_model import OllamaModel
from core.orchestrator import Orchestrator

# --- Page Config ---
st.set_page_config(
    page_title="AI Council",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
# --- Custom CSS ---
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Outfit:wght@500;700&display=swap');

    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        color: #E0E0E0 !important;
    }

    /* Streamlit UI Tweaks */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }

    /* Expander Styling - Glassmorphism */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #E6EDF3 !important;
        font-family: 'Outfit', sans-serif;
    }
    
    .streamlit-expanderContent {
        background-color: transparent;
        border: none;
        padding-left: 1.5rem;
        border-left: 2px solid #58A6FF;
    }

    /* Status Container */
    [data-testid="stStatusWidget"] {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 12px;
    }

    /* Chat Messages */
    [data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Footer & Header cleanup */
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    #stDecoration {display:none;}
    
    /* Custom Header Gradient */
    .main-header {
        font-size: 3rem;
        background: -webkit-linear-gradient(45deg, #4B91F1, #9B72CB);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown('<h2 style="color:#A371F7;">⚙️ Settings</h2>', unsafe_allow_html=True)
    
    # API Key Configuration
    # API Key Configuration
    with st.expander("🔑 API Keys", expanded=False):
        with st.form("api_key_form"):
            api_key = st.text_input("Gemini API Key", value=GEMINI_API_KEY, type="password")
            submitted = st.form_submit_button("Update Key")
            
            if submitted and api_key:
                os.environ["GEMINI_API_KEY"] = api_key
                st.success("Key Updated!")
    
    st.markdown("---")
    st.markdown("### 🏛️ Council Configuration")
    
    # 1. Select Moderator
    available_models = [GEMINI_MODEL] + OLLAMA_MODELS
    # Create display names mapping
    display_names = {m: m.split(":")[0].capitalize() if ":" in m else "Gemini (Cloud)" for m in available_models}
    
    selected_mod_id = st.selectbox(
        "Select Moderator",
        options=available_models,
        format_func=lambda x: f"👑 {display_names[x]}",
        index=0
    )
    
    # 2. Moderator Participation
    mod_participates = st.checkbox(
        "Moderator Joins Round 1?",
        value=True,
        help="If unchecked, the Moderator will ONLY critique and synthesize, effectively acting as purely a judge."
    )

    # 3. Select Panelists
    potential_panelists = [m for m in available_models if m != selected_mod_id]
    
    # Initialize session state for panelist selection if not exists
    if "selected_panelists_set" not in st.session_state:
        st.session_state.selected_panelists_set = set(potential_panelists)
        
    # Ensure set only contains valid potential panelists (in case moderator changed)
    # We keep existing selections if they are still valid potential panelists
    valid_selection = {p for p in st.session_state.selected_panelists_set if p in potential_panelists}
    if not valid_selection: # If empty or invalid, reset to all
         valid_selection = set(potential_panelists)
    st.session_state.selected_panelists_set = valid_selection

    with st.expander("👥 Select Panelists", expanded=False):
        search_query = st.text_input("🔍 Filter models", "", help="Type to find specific models")
        
        st.markdown(f"<small>Selected: {len(st.session_state.selected_panelists_set)}/{len(potential_panelists)}</small>", unsafe_allow_html=True)
        
        # Select All / Deselect All (Optional helper, keeping simple for now as requested)
        
        for p in potential_panelists:
            # Filter logic
            if search_query.lower() in p.lower():
                is_selected = p in st.session_state.selected_panelists_set
                checked = st.checkbox(
                    f"🔸 {display_names[p]}",
                    value=is_selected,
                    key=f"chk_{p}"
                )
                
                # Update State
                if checked:
                    st.session_state.selected_panelists_set.add(p)
                else:
                    st.session_state.selected_panelists_set.discard(p)
                    
    # Convert back to list for usage
    selected_panelists = list(st.session_state.selected_panelists_set)

    st.markdown("---")
    st.markdown("### 👥 Active Panelists")
    
    # Logic to show who is in the panel based on selection
    active_roster = []
    if mod_participates:
        active_roster.append(f"**{display_names[selected_mod_id]}** (Moderator)")
        
    for p in selected_panelists:
        active_roster.append(f"**{display_names[p]}**")
            
    for member in active_roster:
        st.write(f"• {member}")
        
    st.markdown("---")
    if st.button("🗑️ Clear Chat History", type="secondary"):
        st.session_state.conversation = []
        st.rerun()

# --- State Management ---
if "conversation" not in st.session_state:
    st.session_state.conversation = []

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

# --- Helper Functions ---
async def run_meeting(topic, moderator_id, participate_in_r1, panelist_ids):
    """Async wrapper to run the full council meeting"""
    
    # 1. Initialize Objects
    # We need to map IDs to Model Objects
    model_objects = {}
    
    # Gemini
    # Fix: Ensure we pass the API key, not just the model name!
    gemini_key = os.environ.get("GEMINI_API_KEY", GEMINI_API_KEY)
    model_objects[GEMINI_MODEL] = GeminiModel(api_key=gemini_key, model_name=GEMINI_MODEL)
    
    # Ollama
    for name in OLLAMA_MODELS:
        model_objects[name] = OllamaModel(name)
        
    # Select Moderator
    moderator = model_objects[moderator_id]
    
    # Build Council List
    council = []
    
    # Add Moderator if participating
    if participate_in_r1:
        council.append(moderator)
        
    # Add Selected Panelists
    for p_id in panelist_ids:
        if p_id in model_objects:
            council.append(model_objects[p_id])
    
    orchestrator = Orchestrator(council, moderator=moderator)
    
    # 2. UI Layout Containers (For Live View)
    st.markdown("### 🗣️ Round 1: Initial Thoughts")
    r1_container = st.container()
    
    st.markdown("### ⚔️ Round 2: Peer Critique")
    r2_container = st.container()
    
    status_container = st.status("🔔 Calling the Council to order...", expanded=True)
    
    # 3. Callbacks for Streaming UI
    def on_progress(message):
        # Update label instead of writing new lines to prevent jitter
        status_container.update(label=f"🔄 {message}", state="running")
        
    def on_round1_result(model_name, response):
        status_container.write(f"✅ **{model_name}** has spoken.")
        with r1_container:
            with st.expander(f"👤 {model_name}'s Perspective", expanded=False):
                st.markdown(response)

    def on_round2_result(model_name, response):
        status_container.write(f"🛡️ **{model_name}** critiqued.")
        with r2_container:
            with st.expander(f"🕵️ Critique by {model_name}", expanded=False):
                st.markdown(response)
        
    # 4. Run Discussion
    try:
        results = await orchestrator.conduct_discussion(
            topic,
            progress_callback=on_progress,
            on_round1_result=on_round1_result,
            on_round2_result=on_round2_result
        )
        status_container.update(label="✅ Meeting Adjourned!", state="complete", expanded=False)
        return results, orchestrator.moderator.name
    except Exception as e:
        status_container.update(label="❌ Meeting Disrupted!", state="error")
        st.error(f"An error occurred: {str(e)}")
        return None, None
 

# --- Main Interface ---

# Custom Header with Gradient
st.markdown('<h1 class="main-header">🤖 AI Discussion Council</h1>', unsafe_allow_html=True)
st.caption("A multi-model consensus system featuring Gemini, Llama, Mistral, Qwen, and Deepseek.")

# Using a robust display function to handle both strict string messages and rich objects
def render_message(msg):
    with st.chat_message(msg["role"]):
        # Check if this is a rich consensus object
        if msg.get("type") == "consensus_log":
            results = msg["data"]
            moderator_name = msg.get("moderator", "Unknown")
            
            # Reconstruct the view from history
            # Thinking Process Block (Hidden by default)
            with st.expander("💭 View Thinking Process (Council Deliberation)", expanded=False):
                st.markdown("### 🗣️ Round 1: Initial Thoughts")
                for model, text in results.get("round1", {}).items():
                    with st.expander(f"👤 {model}'s Perspective", expanded=False):
                        st.markdown(text)
                
                st.markdown("### ⚔️ Round 2: Peer Critique")
                for model, text in results.get("round2", {}).items():
                    with st.expander(f"🕵️ Critique by {model}", expanded=False):
                        st.markdown(text)

                st.divider()
                st.markdown(f"**Moderated by:** {moderator_name}")
                
                # Transparency: Show the internal reasoning inside the thinking block
                if "moderator_reasoning" in results:
                    st.markdown("#### 🧠 Moderator Reasoning")
                    st.markdown(results["moderator_reasoning"])
                
                # Debugging: Show the raw prompt
                if "synthesis_prompt" in results:
                    with st.expander("📝 View Raw Prompt Data (Debug)", expanded=False):
                        st.caption("This is the exact text sent to the moderator:")
                        st.code(results["synthesis_prompt"], language="text")

            # Final Answer Block (Always Visible)
            st.markdown(f"### 🏆 Final Consensus")
            st.markdown(results.get("final_answer", ""))
            
        else:
            # Standard string message
            st.markdown(msg["content"])

# Render History
for msg in st.session_state.conversation:
    render_message(msg)

# Input Handling
if prompt := st.chat_input("Proposed topic for the council...", disabled=st.session_state.is_processing):
    
    # Add User Message to History
    st.session_state.conversation.append({"role": "user", "content": prompt, "type": "text"})
    # Render immediately (so we don't wait for rerun)
    render_message(st.session_state.conversation[-1])
        
    # Start Processing
    st.session_state.is_processing = True
    
    try:
        # Run output is handled by run_meeting's internal streaming
        results, moderator_name = asyncio.run(run_meeting(prompt, selected_mod_id, mod_participates, selected_panelists))
        
        if results:
            # Save the FULL structured data to history
            st.session_state.conversation.append({
                "role": "assistant",
                "type": "consensus_log",
                "data": results,
                "moderator": moderator_name,
                "content": results.get("final_answer", "") # Fallback content
            })
            
    finally:
        st.session_state.is_processing = False
        st.rerun()

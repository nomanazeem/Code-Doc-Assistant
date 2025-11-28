## Code Doc Assistant

Code Documentation Assistant: Create a tool that helps developers generate and improve code documentation. 
The system indexes a codebase and uses a RAG pipeline to generate docstrings, comments, and high-level documentation. 
Implement multiple agents: one for code parsing and indexing, another for generating documentation
, and a third for ensuring consistency with existing comments. 
Build a command-line interface for easy integration into development workflows.



# Create virtual environment
python3 -m venv CodeDoc_env

# Activate virtual environment
# On macOS/Linux:
source CodeDoc_env/bin/activate


# Install dependencies
pip install -r requirements.txt

# Install python-dotenv if not already installed:
pip install python-dotenv

pip install google-generativeai sentence-transformers python-dotenv click rich numpy scikit-learn


# Set OpenAI API key
export GEMINI_API_KEY="your_gemini_api_key_here"



# Install ONLY the essential packages (no PyTorch, no complex dependencies)
pip install google-generativeai python-dotenv

# Create .env file with your Gemini API key
echo "GEMINI_API_KEY=your_actual_gemini_key_here" > .env

# Make the script executable
chmod +x minimal_doc_assistant.py

# test gemini
python test_gemini.py

# Generate documentation
# Generate documentation for a single file

python clean_doc_assistant.py /Users/nomanazeem/Documents/nisum/Code-Doc-Assistant/minimal_doc_assistant.py --preview


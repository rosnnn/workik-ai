import os
import requests
import re
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_response(user_input):
    """Fetch response from Gemini AI."""
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_input}]
            }
        ]
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        ai_response = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No response received.")
        return ai_response

    except Exception as e:
        return f"❌ Error fetching AI response: {str(e)}"

def extract_code(response):
    """Extract Python code from AI response using regex."""
    match = re.search(r"```python(.*?)```", response, re.DOTALL)
    return match.group(1).strip() if match else None

def is_code_task(user_input):
    """Determine if user input is related to coding."""
    keywords = ["code", "python", "function", "generate", "algorithm", "script", "write a program", "write code"]
    return any(word in user_input.lower() for word in keywords)

def ask_user_confirmation(code):
    """Ask user if they want to execute AI-generated code."""
    print("\nAI has generated the following code:\n")
    print(code)
    user_response = input("\nDo you want to execute this code? (yes/no): ").strip().lower()
    return user_response == "yes"

def log_code(code):
    """Save AI-generated code to a log file."""
    with open("ai_generated_code.log", "a") as f:
        f.write(f"\nGenerated Code:\n{code}\n{'-'*50}\n")

def execute_code(code):
    """Execute AI-generated Python code in a controlled namespace and handle errors."""
    exec_namespace = {}
    try:
        exec(code, exec_namespace)
        return True, None
    except Exception as e:
        print(f"\n❌ Execution failed: {e}")
        return False, str(e)

def refine_code(error_message, original_code):
    """Ask AI to refine code based on execution errors."""
    prompt = f"The following code failed with error: {error_message}. Fix the issue:\n{original_code}"
    return get_ai_response(prompt)

def run_agent():
    print("🤖 AI Agent ready. Type your task (or type 'exit' to quit).\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            print("👋 Goodbye!")
            break

        ai_response = get_ai_response(user_input)
        print("\nAI Response:\n", ai_response)

        code = extract_code(ai_response)

        # 🧠 Only execute if it's a code-related task
        if code and is_code_task(user_input):
            log_code(code)

            if ask_user_confirmation(code):
                success, error = execute_code(code)

                user_feedback = input("\nWas the task successful? (yes/no): ").strip().lower()
                if user_feedback == "yes":
                    print("✅ Task completed successfully. Exiting...")
                    break

                while user_feedback == "no":
                    reason = input("Please describe what went wrong or what needs fixing: ").strip()
                    refined_prompt = f"The following code did not work as expected. Issue: {reason}. Please fix it:\n{code}"
                    refined_response = get_ai_response(refined_prompt)
                    refined_code = extract_code(refined_response)

                    if refined_code:
                        log_code(refined_code)
                        print("\nRefined code:\n", refined_code)
                        if ask_user_confirmation(refined_code):
                            success, error = execute_code(refined_code)
                            user_feedback = input("\nWas the refined task successful? (yes/no): ").strip().lower()
                            if user_feedback == "yes":
                                print("✅ Great! Task now successful. Exiting.")
                                return
                            else:
                                code = refined_code
                        else:
                            print("❌ Execution cancelled by user.")
                            break
                    else:
                        print("❌ Couldn't extract code from AI response.")
                        break
        else:
            print("📝 This doesn't appear to be a code task. Here's the response:\n")
            print(ai_response)

if __name__ == "__main__":
    run_agent()

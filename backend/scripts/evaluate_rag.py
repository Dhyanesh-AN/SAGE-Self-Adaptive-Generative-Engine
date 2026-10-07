# scripts/evaluate_rag.py
import sys
import os
import json
import time

# Force UTF-8 output so emoji don't crash on Windows (cp1252 console)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agent.workflow import AgentWorkflow
from app.integrations.llm.ollama import OllamaProvider

def run_evaluation():
    print("🚀 Starting SAGE Evaluation Suite...")
    
    agent = AgentWorkflow()
    evaluator_llm = OllamaProvider() # We use Llama to grade Llama!

    # 1. Define our Test Dataset
    # Mix some questions that SHOULD be in your resume, and some that SHOULD NOT.
    test_dataset = [
        "What is the main advantage of the microkernel approach to system design?",
        "What is a file-control block (FCB)?",
        "How do you bake a chocolate cake?", # Trick question: Should be caught by Reviewer/Reflector
        "What types of services does the process manager provide in Windows?"
    ]

    results = []

    for idx, question in enumerate(test_dataset, 1):
        print(f"\n--- Test {idx}/{len(test_dataset)} ---")
        print(f"❓ Question: {question}")
        
        start_time = time.time()
        
        # Run the agent
        final_state = agent.run(question)
        
        latency = time.time() - start_time
        answer = final_state.get("answer", "")
        context_chunks = final_state.get("context", [])
        context_text = "\n".join([c.get("text", "") for c in context_chunks])
        
        print(f"⏱️  Latency: {latency:.2f}s")
        print(f"🔄 Retries: {final_state.get('retry_count', 0)}")
        print(f"🤖 Answer: {answer[:100]}...")

        # 2. Grade Faithfulness (Did it hallucinate?)
        faithfulness_prompt = f"""You are an expert AI evaluator. 
        Given the following context and answer, did the answer rely ONLY on the provided context?
        If the answer says "I don't know" or similar, it is faithful.
        
        Context: {context_text}
        Answer: {answer}
        
        Score from 1 to 5 (5 being completely faithful to context, 1 being complete hallucination).
        Output ONLY the integer number.
        """
        try:
            faithfulness_score = int(evaluator_llm.generate(faithfulness_prompt).strip())
        except:
            faithfulness_score = 0
            
        # 3. Grade Answer Relevance (Did it answer the prompt?)
        relevance_prompt = f"""You are an expert AI evaluator. 
        Given the original question and the final answer, does the answer directly address the user's question?
        If the question was unanswerable and the system politely declined, that is a 5.
        
        Question: {question}
        Answer: {answer}
        
        Score from 1 to 5 (5 being perfectly relevant, 1 being completely off-topic).
        Output ONLY the integer number.
        """
        try:
            relevance_score = int(evaluator_llm.generate(relevance_prompt).strip())
        except:
            relevance_score = 0

        print(f"📊 Faithfulness: {faithfulness_score}/5 | Relevance: {relevance_score}/5")
        
        # Record the experiment
        results.append({
            "question": question,
            "latency": latency,
            "retries": final_state.get('retry_count', 0),
            "faithfulness": faithfulness_score,
            "relevance": relevance_score
        })

    # 4. Save the Evaluation Report
    report_path = "evaluation_report.json"
    with open(report_path, "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"\n✅ Evaluation complete! Report saved to {report_path}")

if __name__ == "__main__":
    run_evaluation()
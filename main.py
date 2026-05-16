from Basic import strandsagent
def main():
    print("Hello from strands!")
    
    # result is an AgentResult; print the final answer
    print("\n=== AGENT RESPONSE ===")
    print(strandsagent.callStrandsAgent())


if __name__ == "__main__":
    main()

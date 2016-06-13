
import engine, factory, main, argparse, statistics
# Prep the parser
parser = argparse.ArgumentParser(
    description="Runs statistical analysis on Gravitas")
parser.add_argument("-c", "--config", default="config.json", 
                    help="Name of configuration file.\n"+
                    "Checks for \"config.json\" if not given.\n"+
                    "If configuration file is not found or cannot be\n"+
                    "parsed, an exception is thrown.")
parser.add_argument("-n", "--cycles", type=int, default=200,
                    help="Specifies how many games should be run for analysis.")

def run(cycles, fact):
    # Prepare data containers
    data = {}

    
    # Run the loop
    for cycle in range(cycles):
        # Retrieve the important bits
        (engine, manager) = fact.createHeadless()
        
        # play the game once
        done = False
        while not done:
            # Prepare data-gathering
            while manager.copyState().GMState < manager.GMStates['resolve']:
                if engine.update(): # Run the game up to resolution
                    done = True
                    break # Break the loop if someone has already won
            if done:
                break # No more collections
            while manager.copyState().GMState == manager.GMStates['resolve']:
                if engine.update(): # Finish the resolution step
                    done = True
                    break # Game is over, time to collect data
                    
        # Collect winnerData
        state = manager.copyState()
        winner = state.winner
            
        # increase count of the most recent winner
        if winner in data:
            data[winner] += 1
        else:
            data[winner] = 0

    print(data)

# Runtime bit
if __name__ == "__main__":
    # Do the parsering
    args = parser.parse_args()
    # Do the other parsering
    margs = main.parser.parse_args(['-c', args.config, '--headless', '-l', '0'])
    # Factorize the factory
    fact = factory.Factory(margs)
    # Launch the run
    run(args.cycles, fact)

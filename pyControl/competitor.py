import random

class Competitor():
    def __init__(self):
        
        history_length = 3 # We are looking at patterns of up to 3 trials
        # Trials consist of 2 bits of information, a L/R choice and rewarded/not rewarded outcome.
        # Therefore every trial will be 1 of 4 possible combinations of choice and outcome
        outcome_combinations = 4
        
        # create zeroed arrays that will hold the pattern counts and conditional left counts
        self.pattern_counts = [[0 for i in range(outcome_combinations ** j)] for j in range(1, history_length+1)] 
        self.left_conditional_counts = [[0 for i in range(outcome_combinations ** j)] for j in range(1, history_length+1)]
        #initialize history windows
        self.choice_history = [0 if random.random() < 0.5 else 1 for i in range(history_length)]
        self.reward_history = [0 if random.random() < 0.5 else 1 for i in range(history_length)]
        
        
    def update_competitor(self,choice,reward,debug=False):
        trial_history = [''.join([str(self.choice_history[i]) + str(self.reward_history[i]) for i in range(j)]) for j in range(1, 4)]
        patterns = [int(pattern,2) for pattern in trial_history]
    
        for group,pattern_id in enumerate(patterns):
            self.pattern_counts[group][pattern_id] += 1
            if choice == 1:
                self.left_conditional_counts[group][pattern_id] += 1
        
        if debug:
            print("choices",self.choice_history,"rewards",self.reward_history)
            print(trial_history,"==>",patterns)
            print("--patterns--\n",self.pattern_counts)
            print("--conditional lefts--\n",self.left_conditional_counts)
                
        # update recent histories. it is a rolling window of last 3 trials
        if choice == 'L':
            self.choice_history.append(1) # add new trial
        else:
            self.choice_history.append(0) # add new trial

        self.choice_history = self.choice_history[1:] #trim first trial
        
        if reward == "B" or reward =="C":
            self.reward_history.append(1)
        else:
            self.reward_history.append(0)
        self.reward_history = self.reward_history[1:]
        
        
    def recur_factorial(self, f):
        # https://www.tutorialspoint.com/factorial-in-python#:~:text=%20factorial%20%28%29%20in%20Python%20%201%20Using,8%20Example.%20%209%20Outputs.%20%20More%20
        if f == 1:
            return f
        elif f == 0:
            return 1
        elif f < 1:
            return ("NA")
        else:
            return f * self.recur_factorial(f - 1)

    def nchoosek(self, n, k):
        return self.recur_factorial(n) / (self.recur_factorial(k) * self.recur_factorial(n - k))

    def binompdf(self, k: int, n: int, p: float):
        return self.nchoosek(n, k) * p ** k * (1 - p) ** (n - k)

    def binomcdf(self, k, n, p):
        return sum([self.binompdf(kk, n, p) for kk in range(k + 1)])
    
    def predict(self,debug=False):
        cdf = []
        recent_history = [''.join([str(self.choice_history[i]) + str(self.reward_history[i]) for i in range(j)]) for j in range(1, 4)]
        patterns = [int(pattern,2) for pattern in recent_history]

        for i, j in enumerate(patterns):
            cdf.append(self.binomcdf(self.left_conditional_counts[i][j],self.pattern_counts[i][j],0.5))

        # I don't understand what's going on here:
        probabilities = [abs(i-0.5) for i in cdf]
        prediction = int(cdf[probabilities.index(max(probabilities))] > 0.5)     

        if debug:
            print("pattern {}".format(patterns))
            print("cdf",str(cdf))
            print("?",str(probabilities))
            print('Prediction: ' + str(prediction))

        if prediction:
            return 'L'
        else:
            return 'R'

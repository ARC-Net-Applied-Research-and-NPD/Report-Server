import matplotlib.pyplot as plt 
import json 
import matplotlib# Assume a 5-point scale
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use('Agg')  # Non-interactive backend


def generate_radar_chart(output_path='radar_chart.png'):
    values = []
    labels = []
    with open(r'json/scores.json' , 'r') as fp:
        data = json.load(fp)
    items = list(data.items()) 
    print("Items: ", items)
    print(items[-1][1])
    values.append(items[-1][1])
    labels.append(items[-1][0])
    values.append(items[-2][1])
    labels.append(items[-2][0])
    values.append(items[-3][1])
    labels.append(items[-3][0])
    values.append(items[-4][1])
    labels.append(items[-4][0])
    print("Values: ", values)
    print("Labels: ", labels)
    plt.plot(labels, values, marker="s")
    plt.grid(axis='x', which='both', linestyle='-', linewidth=1.5, color='gray', alpha=0.6)
    plt.tight_layout()
    plt.xlabel("Parameters")
    plt.ylabel("Percentage") 
    plt.title("Scores", fontsize=16, fontweight='bold' )
    ax = plt.gca()  
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.savefig(output_path, bbox_inches='tight', pad_inches=0.2)
    plt.close()



# generate_radar_chart("output.png")
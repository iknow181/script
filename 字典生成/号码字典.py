import random

def generate_phone_numbers(num_entries, filename):
    with open(filename, 'w') as f:
        for _ in range(num_entries):
            # Generate a random 7-digit number as string
            num = '0' + str(random.choice([1, 2])) + ''.join(str(random.randint(0, 9)) for _ in range(5))
            f.write(num + '\n')  # Writing each number on a new line

# Generate and write 100 phone numbers to 'phone_numbers.txt'
generate_phone_numbers(100, 'phone_numbers.txt')

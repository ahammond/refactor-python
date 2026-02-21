import json
import csv

# Global variables
data = []
THRESHOLD = 100

def process_users(file='users.csv', filters=[]):
    # Read and process user data
    f = open(file, 'r')
    reader = csv.DictReader(f)

    for row in reader:
        data.append(row)

    # Process the data
    results = []
    for d in data:
        age = int(d['age'])
        if age > 18:
            score = calculate_score(d['purchases'], d['visits'])
            if score > THRESHOLD:
                results.append(d)

    # Apply filters
    for filter in filters:
        filter['count'] = filter.get('count', 0) + 1

    f.close()
    return results

def calculate_score(p, v):
    # Calculate user score
    return int(p) * 10 + int(v) * 5

def generate_report(users, output='report.txt'):
    # Generate report
    f = open(output, 'w')

    total = 0
    avg = 0

    for u in users:
        total = total + 1
        s = calculate_score(u['purchases'], u['visits'])
        f.write(f"User: {u['name']}, Score: {s}\n")

    if total > 0:
        avg = sum([calculate_score(u['purchases'], u['visits']) for u in users]) / total

    f.write(f"\nTotal users: {total}\n")
    f.write(f"Average score: {avg}\n")

    f.close()
    return True

def export_json(users, file='output.json'):
    # Export to JSON
    f = open(file, 'w')
    json.dump(users, f)
    f.close()

def main():
    users = process_users()
    generate_report(users)
    export_json(users)
    print('Done!')

if __name__ == '__main__':
    main()


# ============================================================================
# Skeleton functions/classes for test compatibility
# These are placeholders that should be implemented during refactoring.
# Function signatures are provided to guide the refactoring.
# ============================================================================

class UserDataError(Exception):
    pass


class ScoringConfig:
    def __init__(self, purchase_weight: int = 10, visit_weight: int = 5):
        raise NotImplementedError(f"ScoringConfig.__init__ called")


def read_users_from_csv(filepath: str = 'users.csv') -> list:
    raise NotImplementedError(f"read_users_from_csv called")


def calculate_user_score(purchases: str, visits: str, config: ScoringConfig = None) -> int:
    raise NotImplementedError(f"calculate_user_score called")

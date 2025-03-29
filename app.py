from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/split', methods=['POST'])
def split():
    descriptions = request.form.getlist('description')
    amounts = request.form.getlist('amount')
    paid_by = request.form.getlist('paid_by')

    transactions = []
    total_amount = 0
    for i in range(len(descriptions)):
        amount = float(amounts[i])
        total_amount += amount
        transactions.append({
            'description': descriptions[i],
            'amount': amount,
            'paid_by': paid_by[i]
        })

    num_friends = len(set(paid_by))
    equal_share = total_amount / num_friends

    net_amounts = calculate_net_amounts(transactions, equal_share, num_friends)
    minimized_transactions = minimize_cash_flow(net_amounts)

    return render_template('result.html', transactions=minimized_transactions, total_amount=total_amount)

def calculate_net_amounts(transactions, equal_share, num_friends):
    net_amounts = {friend: -equal_share for friend in set(transaction['paid_by'] for transaction in transactions)}

    for transaction in transactions:
        paid_by = transaction['paid_by']
        amount = transaction['amount']

        if paid_by not in net_amounts:
            net_amounts[paid_by] = 0

        net_amounts[paid_by] += amount

    return net_amounts

def minimize_cash_flow(net_amounts):
    creditors = []  #someone who has paid more than their share, so will receive money
    debtors = []    #someone who has paid less than their share, will give money

    for person, amount in net_amounts.items():
        if amount > 0:
            creditors.append((person, amount))
        elif amount < 0:
            debtors.append((person, -amount))

    transactions = []

    while creditors and debtors:
        creditor = creditors[-1]
        debtor = debtors[-1]

        amount = min(creditor[1], debtor[1])

        transactions.append({
            'from': debtor[0],
            'to': creditor[0],
            'amount': amount
        })

        creditors[-1] = (creditor[0], creditor[1] - amount)
        debtors[-1] = (debtor[0], debtor[1] - amount)

        if creditors[-1][1] == 0:
            creditors.pop()
        if debtors[-1][1] == 0:
            debtors.pop()

    return transactions

if __name__ == '__main__':
    app.run()

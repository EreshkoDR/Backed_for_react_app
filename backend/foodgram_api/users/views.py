from django.shortcuts import render


def main(requests):
    return render(requests, context={'test': 'Testing'})

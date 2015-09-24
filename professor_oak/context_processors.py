import random

def skynet(request):
    """Show some humorous message related to Terminator movies."""
    is_jake = request.user.email in [
        'mark.wolf.music@gmail.com',
        'plews2@uic.edu',
        'lapping1@uic.edu',
    ]
    saving_throw = random.randrange(0, 20)
    skynet = (is_jake and not saving_throw)
    return {'skynet': skynet}

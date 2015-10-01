import random

def skynet(request):
    """Show some humorous message related to Terminator movies."""
    jake_emails = [
        # 'mark.wolf.music@gmail.com',
        # 'plews2@uic.edu',
        'lapping1@uic.edu',
    ]
    is_jake = (not request.user.is_anonymous()) and (request.user.email in jake_emails)
    saving_throw = random.randrange(0, 20)
    skynet = (is_jake and not saving_throw)
    return {'skynet': skynet}

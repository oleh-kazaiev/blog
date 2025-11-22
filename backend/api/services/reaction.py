from django.db.models import Count

from blog.models import PostReaction
from users.notifications import send_reaction_notification


def toggle_reaction(post, user, reaction_type):
    """
    Toggle a reaction on a post for a user.

    Args:
        post: The Post object.
        user: The User object.
        reaction_type: The type of reaction

    Returns:
        dict: Result containing status, action, and updated counts.
    """
    valid_reactions = set(dict(PostReaction.REACTION_CHOICES))

    if reaction_type not in valid_reactions:
        raise ValueError('Invalid reaction type')

    existing_reaction = PostReaction.objects.filter(post=post, user=user).first()

    if existing_reaction:
        if existing_reaction.reaction_type == reaction_type:
            existing_reaction.delete()
            action = 'removed'
        else:
            existing_reaction.reaction_type = reaction_type
            existing_reaction.save(update_fields=['reaction_type'])
            action = 'changed'
    else:
        PostReaction.objects.create(
            post=post,
            user=user,
            reaction_type=reaction_type
        )
        action = 'added'
        send_reaction_notification(post, user.email, reaction_type)

    counts = PostReaction.objects.filter(post=post).values('reaction_type').annotate(count=Count('id'))

    return {
        'status': 'success',
        'action': action,
        'counts': {c['reaction_type']: c['count'] for c in counts},
    }

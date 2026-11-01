"""Buffer API connection checks. No publication mutations in the preflight."""
import json
import os
import urllib.request

CHANNEL_ID = '6ae78a17e29c69a1712b879a'
USERNAME = 'retovisual70'


def query(document, variables=None):
    token = os.environ.get('BUFFER_API_KEY', '').strip()
    if not token:
        raise RuntimeError('BUFFER_API_KEY is not configured')
    request = urllib.request.Request('https://api.buffer.com',
        data=json.dumps({'query': document, 'variables': variables or {}}).encode(),
        headers={'Authorization': 'Bearer '+token, 'Content-Type': 'application/json'}, method='POST')
    # No automatic retries: a publication response can be ambiguous.
    try:
        with urllib.request.urlopen(request, timeout=40) as response:
            result = json.load(response)
    except Exception as exc:
        raise RuntimeError('Buffer request failed; reconcile before retrying') from None
    if result.get('errors'):
        messages = [e.get('message', 'GraphQL error').replace(token, '[redacted]') for e in result['errors']]
        raise RuntimeError('Buffer: '+ '; '.join(messages))
    return result['data']


def preflight(schema=False):
    orgs = query('query { account { organizations { id } } }')['account']['organizations']
    matches = []
    for org in orgs:
        channels = query('query($org: OrganizationId!) { channels(input:{organizationId:$org}) { id name displayName service isQueuePaused } }', {'org': org['id']})['channels']
        for channel in channels:
            if channel['id'] == CHANNEL_ID:
                matches.append((org['id'], channel))
    if len(matches) != 1:
        raise RuntimeError('Expected TikTok channel was not uniquely found')
    org_id, channel = matches[0]
    if channel['service'].lower() != 'tiktok' or channel['name'].lstrip('@').lower() != USERNAME:
        raise RuntimeError('Wrong destination account')
    if channel['isQueuePaused']:
        raise RuntimeError('Buffer queue is paused')
    result = {'status':'CONNECTION_READ_VERIFIED', 'organization_id':org_id, 'channel':channel,
              'published':False, 'scheduled':False, 'publishing_enabled':False}
    print(json.dumps(result, ensure_ascii=False))
    if schema:
        for name in ['CreatePostInput','PostInputMetaData','TikTokPostMetadataInput','PostInput','Post','PostStatus']:
            info = query('query($name:String!) { __type(name:$name) { name inputFields { name type { name kind ofType { name kind } } } fields { name type { name kind ofType { name kind } } } enumValues { name } } }', {'name':name})
            print(json.dumps(info))
    return result


POST_FIELDS = 'id channelId dueAt status schedulingType text externalLink assets { source } metadata { ... on TiktokPostMetadata { isAiGenerated } }'


def read_post(post_id):
    return query('query($input:PostInput!) { post(input:$input) { '+POST_FIELDS+' } }', {'input':{'id':post_id}})['post']


def create_post(payload):
    result = query('mutation($input:CreatePostInput!) { createPost(input:$input) { ... on PostActionSuccess { post { '+POST_FIELDS+' } } ... on MutationError { message } } }', {'input':payload})['createPost']
    if not result.get('post'):
        raise RuntimeError('Buffer rejected the post; reconcile before retrying: '+result.get('message','Unknown result'))
    return result['post']


if __name__ == '__main__':
    preflight()

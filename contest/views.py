from django.shortcuts import render
from .models import Contest, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import CommentForm
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from datetime import datetime, timezone
from django.db.models import Q
from django.db.models import Count




def contest_list(request):
    category_filter = request.GET.get('category', None)
    if category_filter:
        contests = Contest.objects.filter(contest_category=category_filter).order_by('-pk')
    else:
        contests = Contest.objects.order_by('-pk')

    today = datetime.now().date()

    for contest in contests:
        contest.deadline = (contest.deadline - today).days
        contests = contests.annotate(comments_count=Count('comment'))

    page = request.GET.get('page', 1)
    paginator = Paginator(contests, 8)


    try:
        contests = paginator.page(page)
    except PageNotAnInteger:
        contests = paginator.page(1)
    except EmptyPage:
        contests = paginator.page(paginator.num_pages)

    return render(request, 'contest/contest_list.html', {'contests': contests, 'page_obj': contests})
    
    
def contest_detail(request, contest_id):
    contest = Contest.objects.get(id=contest_id)
    
    contest.contest_view_count += 1
    contest.save()

    # Initialize or retrieve the 'viewed_contests' list in the session
    viewed_contests = request.session.get('viewed_contests', [])
    
    # Add the contest_id to the 'viewed_contests' list in the session if not already present
    if contest_id not in viewed_contests:
        viewed_contests.append(contest_id)
        request.session['viewed_contests'] = viewed_contests
        request.session.modified = True
        
    comments_count = Comment.objects.filter(contest_post=contest).count()
    
    return render(request, 'contest/contest_detail.html', {'contest': contest, 'comments_count': comments_count})


@require_POST
@login_required
def scrap_contest(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)

    # 사용자가 이미 해당 콘테스트를 스크랩한 경우 중복을 피하기 위해 체크
    if request.user in contest.scraped_by_users.all():
        return JsonResponse({'status': 'error', 'message': '이미 스크랩한 공모전입니다'})

    # 현재 사용자를 스크랩한 사용자 목록에 추가
    contest.scraped_by_users.add(request.user)

    return JsonResponse({'status': 'success', 'message': '공모전이 스크랩되었습니다'})


from django.utils import timezone

def comment(request, contest_id):
    contest = Contest.objects.get(id=contest_id)
    comments = Comment.objects.filter(contest_post=contest)
    
    if request.method == "POST":
        comment_text = request.POST.get('comment', '')  # 'comment' 필드의 값을 가져옴
        if comment_text:  # 댓글이 비어있지 않은 경우에만 처리
            comment = Comment()
            comment.comment = comment_text
            comment.created_at = timezone.now()
            comment.contest_post = contest  # contest_post 필드에 Contest 객체 할당
            comment.save()
    
    return render(request, 'contest/comment.html', {'comments': comments, 'contest': contest})


#검색
def searchResult(request):
    if 'q' in request.GET:
        query = request.GET.get('q')
        contests = Contest.objects.filter(
            Q(contest_title__icontains=query) |
            Q(contest_description__icontains=query) |
            Q(contest_category__icontains=query)
        )
        return render(request, 'contest/contest_search.html', {'query': query, 'contests': contests})
    else:
        return render(request, 'contest/contest_search.html')
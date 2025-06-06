# 사내 게시판, 설문조사, 온라인 시험 등 각종 시스템에 활용할 수 있는 공통 모델로, 오앤에스 사내 템플릿을 만드는 프로젝트 입니다.
#### ex) 네이버 설문폼과 같이 유저가 자유롭게 형식을 선택하여 입력할 수 있는 양식으로 만들고자 합니다.
## 이 프로젝트는 Django templates, Bootstrap, HTMX를 활용하여 구현하였습니다.

#### 업데이트 2025.04.22 잔여 기능 : 설문 제출 완료 후 뒤로가기 클릭 시 다시 설문 페이지로 넘어가는 문제

## 요청사항
1. **Contents 관리의 효율화**
   1. 현재 모델 구조는 Text, Image, File 등을 개별 모델로 관리하며, GenericForeignKey를 사용하여 접근하고 있습니다. 
     이 경우 각 컨텐츠에 대한 관리는 용이하지만, 컨텐츠 생성 시 
     ` post_content = PostContent.objects.create(post_id=request.POST.get('post'),content=content)` 등과 같은 관리용 추가 코드가 필요합니다.
     좀 더 효율적으로 컨텐츠를 관리할 수 있는 방법이 있을지 궁금합니다.

2. **HTMX 사용 관련**
   1. 현재 HTMX 적용 시 view에서 form 유효성 검사 후 if self.request.headers.get('HX-Request'):를 통해 Header 검사 후 partials templates으로 응답하고 있는데,
      HTMX 동작에 대해 header를 읽어서 동작을 별도 구현하는 방식보다 더 효율적으로 제어할 수 있는 방법이 있는지 궁금합니다.
   2. 폼 제출 시 js가 동작하는 코드에 대해서 htmx로 대체할 수 있는 방법이 있을지 궁금합니다.

3. **동적 폼 생성 및 렌더링**
   1. django model formset/form factory 을 활용하여 post, contents, option 등 여러 유형의 모델을 동시에 생성하는 템플릿을 만들고자 하였으나,
      여러 종류의 모델을 동시에 form으로 제어하는 것이 쉽지 않아, view에서 직접 모델 유형별 form을 처리하고 있습니다.
      여러 유형의 form을 더 효율적으로 제어할 수 있는 방법이 있을지 궁금합니다.
   
4. **대용량 데이터 처리를 위한 유저 입력 효율화**
   1. 현재는 선택지가 있는 문항(객관식)의 경우 문항 단위로 유저가 Post/Patch 하도록 되어있습니다.
      선택지가 없이 서술식으로 된 문항의 경우에는 유저가 '임시저장' 버튼을 누르면 Post/Patch 되고, 
      별도 유저의 동작이 없는 경우 마지막 최종 form 제출 시 post/patch 되도록 구현되어 있습니다.
      그러나 이후 대규모 유저 데이터 처리 시, 동시에 post/patch가 발생할 경우 서버 부하가 발생할 우려가 있어,
      자원 사용을 최소화하며 가장 효율적으로 form submit을 처리할 수 있는 방법이 있을지 궁금합니다.

5. **도커기반으로 위의 솔루션을 배포과정과 스케일링 전략에 대한 조언**
   1. 위의 솔루션은 결국 배포가 되어야 할 것이고, 유져규모에 따라 스케일아웃 또는 스케일업을 해야할텐데,
      이 프로젝트를 통해 그 과정을 경험할 수 잇으면 좋겠습니다.

## 프로젝트 설명
1. **모델**
   1. Text, Image, File, Content : GenericForeignKey를 활용하여 컨텐츠를 별도로 관리하는 모델
   2. PostType, MainPost, SubPost : 게시글 내용 및 유형 관리
   3. PostContent : 게시글과 컨텐츠를 연결하는 중간 모델
   4. PostOptions : 객관식 보기와 같은 선택지를 관리하는 모델
   5. UserAnswer : 유저가 작성한 답변을 관리하는 모델
   6. MultiSubjectiveAnswers : 서술형 답변 중 1-1, 1-2, ... 등과 같이 1개의 SubPost에 여러개의 답변이 있을 때 저장하는 모델

2. **Template**
   1. post_list, form, detail : 게시글 목록, 작성, 수정 템플릿 (대주제)
   2. post_content_form, content_forms folder : 게시글에 포함된 컨텐츠를 유저 선택에 따라 동적 렌더링
   3. sub_post : 실제 게시글의 내용을 담을 템플릿 (질문 문항 등)
   4. post_options : 객관식 보기와 같이 선택지를 렌더링 할 수 있는 템플릿

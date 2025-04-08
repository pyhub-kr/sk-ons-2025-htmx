# 사내 게시판, 설문조사, 온라인 시험 등 각종 시스템에 활용할 수 있는 공통 모델을 만드는 프로젝트 입니다.
#### ex) 네이버 설문폼과 같은 양식으로 구현해보려고 합니다.
## 이 프로젝트는 Django templates, Bootstrap, HTMX를 활용하여 구현하였습니다.

## 요청사항
1. **Contents 관리의 효율화**
   1. 현재 모델 구조는 Text, Image, File 등을 개별 모델로 관리하며, GenericForeignKey를 사용하여 접근하고 있습니다. 
     이 경우 각 컨텐츠에 대한 관리는 용이하지만, 컨텐츠 생성 시 
     ` post_content = PostContent.objects.create(post_id=request.POST.get('post'),content=content)` 등과 같은 관리용 추가 코드가 필요합니다.
     좀 더 효율적으로 컨텐츠를 관리할 수 있는 방법이 있을지 궁금합니다.

2. **HTMX 사용 관련**
   1. 현재 HTMX 적용 시 view에서 form 유효성 검사 후 if self.request.headers.get('HX-Request'):를 통해 Header 검사 후 partials templates으로 응답하고 있는데,
      HTMX 동작에 대해 header를 읽어서 동작을 별도 구현하는 방식보다 더 효율적으로 제어할 수 있는 방법이 있는지 궁금합니다.

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
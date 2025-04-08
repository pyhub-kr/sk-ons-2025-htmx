# 사내 게시판, 설문조사, 온라인 시험 등 각종 시스템에 활용할 수 있는 공통 모델을 만드는 프로젝트 입니다.
## 이 프로젝트는 Django templates, Bootstrap, HTMX를 활용하여 구현하였습니다.

## 요청사항
1. **Contents 관리의 효율화**
   1. 현재 모델 구조는 Text, Image, File 등을 개별 모델로 관리하며, GenericForeignKey를 사용하여 접근하고 있습니다. 
     이 경우 각 컨텐츠에 대한 관리는 용이하지만, 컨텐츠 생성 시 
     ` post_content = PostContent.objects.create(post_id=request.POST.get('post'),content=content)` 등과 같은 관리용 추가 코드가 필요합니다.
     좀 더 효율적으로 컨텐츠를 관리할 수 있는 방법이 있을지 궁금합니다.

2. **HTMX 사용 관련**
   1. 현재 HTMX 적용 시 view에서 form 유효성 검사 후 if self.request.headers.get('HX-Request'):를 통해 Header 검사 후 partials templates으로 응답하고 있는데,

3. **동적 폼 생성 및 렌더링**
   1. django model formset을 활용하여 post, contents, option 등 여러 모델을 동시에 생성하는 템플릿을 만들고자 하였으나,
      현재는 원하는대로 컨트롤이 되지 않아 각각 모델 별로 CRUD 하도록 구현되어 있습니다.
      더 효율적으로 formset을 활용할 수 있는 방법이 있을지 궁금합니다.
   
4. 
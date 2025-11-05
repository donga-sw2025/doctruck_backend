"""Document Resource - Flask-RESTful API 엔드포인트

Spring Boot와 비교:
- Resource = @RestController
- get() = @GetMapping
- 공개 API (인증 불필요) - Spring의 permitAll()과 유사

Spring 예시:
@RestController
@RequestMapping("/api/v1/documents")
public class DocumentController {
    @GetMapping
    public List<DocumentDto> list() { }

    @GetMapping("/{id}")
    public DocumentDto getById(@PathVariable Long id) { }
}
"""

from flask import request
from flask_restful import Resource
from sqlalchemy import or_

from doctruck_backend.api.schemas import DocumentSchema
from doctruck_backend.models import Document
from doctruck_backend.models.document import DocumentStatus, DocumentType
from doctruck_backend.extensions import db
from doctruck_backend.commons.pagination import paginate
from datetime import datetime


class DocumentResource(Resource):
    """단일 공문서 리소스 - 상세 조회

    ---
    get:
      tags:
        - documents
      summary: 공문서 상세 조회
      description: 특정 공문서의 상세 정보를 조회합니다 (일반 사용자는 VERIFIED 문서만 조회 가능)
      parameters:
        - in: path
          name: doc_id
          schema:
            type: integer
          required: true
          description: 공문서 ID
      responses:
        200:
          description: 공문서 상세 정보
          content:
            application/json:
              schema:
                type: object
                properties:
                  document:
                    $ref: '#/components/schemas/DocumentSchema'
        404:
          description: 공문서를 찾을 수 없음
    """

    # 인증 불필요 (공개 API)

    def get(self, doc_id):
        """공문서 상세 조회 (Spring의 @GetMapping과 유사)"""
        schema = DocumentSchema()
        document = Document.query.get_or_404(doc_id)

        # 사용자는 VERIFIED 문서만 조회 가능
        # (관리자 API는 나중에 별도 구현)
        if document.status != DocumentStatus.VERIFIED:
            return {"message": "검증된 공문서만 조회할 수 있습니다."}, 403

        return {"document": schema.dump(document)}, 200


class DocumentList(Resource):
    """공문서 목록 조회 - 필터링 및 검색 지원

    ---
    get:
      tags:
        - documents
      summary: 공문서 목록 조회
      description: VERIFIED 상태의 공문서 목록을 조회합니다 (페이지네이션 및 필터링 지원)
      parameters:
        - in: query
          name: document_type
          schema:
            type: string
            enum: [POLICY, NOTICE, REGULATION, EVENT, OTHER]
          required: false
          description: 공문서 유형 필터
        - in: query
          name: source
          schema:
            type: string
          required: false
          description: "출처 필터 (예: 서울시청)"
        - in: query
          name: start_date
          schema:
            type: string
            format: date
          required: false
          description: 게시일 시작 필터 (YYYY-MM-DD)
        - in: query
          name: end_date
          schema:
            type: string
            format: date
          required: false
          description: 게시일 종료 필터 (YYYY-MM-DD)
        - in: query
          name: search
          schema:
            type: string
          required: false
          description: 검색어 (제목 또는 AI 요약)
        - in: query
          name: page
          schema:
            type: integer
            default: 1
          description: 페이지 번호
        - in: query
          name: per_page
          schema:
            type: integer
            default: 10
          description: 페이지당 개수
      responses:
        200:
          description: 공문서 목록
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/PaginatedResult'
                  - type: object
                    properties:
                      results:
                        type: array
                        items:
                          $ref: '#/components/schemas/DocumentSchema'
    """

    # 인증 불필요 (공개 API)

    def get(self):
        """공문서 목록 조회 (필터링 지원 - Spring의 @GetMapping + @RequestParam과 유사)"""
        schema = DocumentSchema(many=True)

        # 기본 쿼리: VERIFIED 문서만
        # Spring에서는 JPA Specification 또는 @Query로 구현
        query = Document.query.filter_by(status=DocumentStatus.VERIFIED)

        # 1. 공문서 유형 필터 (Spring의 @RequestParam)
        document_type = request.args.get("document_type")
        if document_type:
            try:
                document_type_enum = DocumentType[document_type.upper()]
                query = query.filter(Document.document_type == document_type_enum)
            except KeyError:
                return {"message": f"Invalid document_type: {document_type}"}, 400

        # 2. 출처 필터
        source = request.args.get("source")
        if source:
            query = query.filter(Document.source.ilike(f"%{source}%"))

        # 3. 날짜 범위 필터 (게시일 기준)
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
                query = query.filter(Document.published_at >= start_date_obj)
            except ValueError:
                return {"message": "Invalid start_date format. Use YYYY-MM-DD"}, 400

        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
                query = query.filter(Document.published_at <= end_date_obj)
            except ValueError:
                return {"message": "Invalid end_date format. Use YYYY-MM-DD"}, 400

        # 4. 검색어 필터 (제목 또는 AI 요약에서 검색)
        # Spring의 JPA Specification과 유사
        search = request.args.get("search")
        if search:
            search_filter = or_(
                Document.title.ilike(f"%{search}%"),
                Document.ai_summary.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        # 5. 최신순 정렬 (게시일 기준)
        # Spring의 Sort.by(Sort.Direction.DESC, "publishedAt")와 유사
        query = query.order_by(Document.published_at.desc())

        # 6. 페이지네이션 (Spring의 Pageable과 유사)
        return paginate(query, schema)

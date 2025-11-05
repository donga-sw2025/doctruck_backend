"""Admin Document Resource - 관리자 전용 공문서 관리 API

Spring Boot와 비교:
- Resource = @RestController
- admin_required = @PreAuthorize("hasRole('ADMIN')")

Spring 예시:
@RestController
@RequestMapping("/api/v1/admin/documents")
@PreAuthorize("hasRole('ADMIN')")
public class AdminDocumentController {
    @GetMapping("/pending")
    public List<DocumentDto> getPendingDocuments() { }

    @PutMapping("/{id}/verify")
    public DocumentDto verifyDocument(@PathVariable Long id) { }
}
"""

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from datetime import datetime

from doctruck_backend.api.schemas import DocumentSchema
from doctruck_backend.models import Document
from doctruck_backend.models.document import DocumentStatus
from doctruck_backend.extensions import db
from doctruck_backend.commons.pagination import paginate
from doctruck_backend.api.admin_helpers import admin_required, get_admin_id


class AdminDocumentPending(Resource):
    """PENDING 문서 목록 (검증 대시보드)

    ---
    get:
      tags:
        - admin-documents
      summary: 검증 대기 문서 목록 조회 (관리자 전용)
      description: 관리자 검증을 위한 PENDING 상태 문서 목록을 조회합니다
      responses:
        200:
          description: PENDING 문서 목록
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
        403:
          description: Admin permission required
    """

    method_decorators = [admin_required, jwt_required()]

    def get(self):
        """PENDING 문서 목록 조회 (관리자용)"""
        schema = DocumentSchema(many=True)
        query = Document.query.filter_by(status=DocumentStatus.PENDING).order_by(Document.created_at.desc())
        return paginate(query, schema)


class AdminDocumentVerify(Resource):
    """문서 검증 처리 (승인/반려)

    ---
    put:
      tags:
        - admin-documents
      summary: 문서 검증 처리 (관리자 전용)
      description: PENDING 문서를 VERIFIED(승인) 또는 REJECTED(반려)로 변경합니다
      parameters:
        - in: path
          name: doc_id
          schema:
            type: integer
          required: true
          description: 문서 ID
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                action:
                  type: string
                  enum: [approve, reject]
                  required: true
                  description: approve (승인) or reject (반려)
                rejection_reason:
                  type: string
                  description: 반려 사유 (action=reject일 때 필수)
      responses:
        200:
          description: 검증 처리 완료
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                  document:
                    $ref: '#/components/schemas/DocumentSchema'
        400:
          description: Bad request
        403:
          description: Admin permission required
        404:
          description: Document not found
    """

    method_decorators = [admin_required, jwt_required()]

    def put(self, doc_id):
        """문서 검증 처리 (승인 또는 반려)"""
        document = Document.query.get_or_404(doc_id)

        if document.status != DocumentStatus.PENDING:
            return {"message": "PENDING 상태의 문서만 검증할 수 있습니다."}, 400

        action = request.json.get("action")
        if action not in ["approve", "reject"]:
            return {"message": "action은 'approve' 또는 'reject'여야 합니다."}, 400

        admin_id = get_admin_id()

        if action == "approve":
            document.status = DocumentStatus.VERIFIED
            document.verified_by_admin_id = admin_id
            document.verified_at = datetime.utcnow()
            message = "문서가 승인되었습니다."

        else:  # reject
            rejection_reason = request.json.get("rejection_reason")
            if not rejection_reason:
                return {"message": "반려 시 rejection_reason이 필요합니다."}, 400

            document.status = DocumentStatus.REJECTED
            document.verified_by_admin_id = admin_id
            document.verified_at = datetime.utcnow()
            # rejection_reason 필드가 없으므로 ai_summary에 추가 기록 (임시)
            document.ai_summary = f"[REJECTED: {rejection_reason}]\n\n{document.ai_summary or ''}"
            message = "문서가 반려되었습니다."

        db.session.commit()

        schema = DocumentSchema()
        return {"message": message, "document": schema.dump(document)}, 200


class AdminDocumentList(Resource):
    """전체 문서 목록 (관리자용 - 상태 무관)

    ---
    get:
      tags:
        - admin-documents
      summary: 전체 문서 목록 조회 (관리자 전용)
      description: 상태와 무관하게 모든 문서 목록을 조회합니다
      parameters:
        - in: query
          name: status
          schema:
            type: string
            enum: [PENDING, VERIFIED, REJECTED]
          required: false
          description: 상태 필터
      responses:
        200:
          description: 전체 문서 목록
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
        403:
          description: Admin permission required
    """

    method_decorators = [admin_required, jwt_required()]

    def get(self):
        """전체 문서 목록 조회 (관리자용 - 상태 필터 가능)"""
        schema = DocumentSchema(many=True)
        query = Document.query

        # 상태 필터 (선택)
        status_filter = request.args.get("status")
        if status_filter:
            try:
                status_enum = DocumentStatus[status_filter.upper()]
                query = query.filter_by(status=status_enum)
            except KeyError:
                return {"message": f"Invalid status: {status_filter}"}, 400

        query = query.order_by(Document.created_at.desc())
        return paginate(query, schema)


class AdminDocumentResource(Resource):
    """문서 수정/삭제 (관리자용)

    ---
    put:
      tags:
        - admin-documents
      summary: 문서 수정 (관리자 전용)
      description: 문서 정보를 수정합니다
      parameters:
        - in: path
          name: doc_id
          schema:
            type: integer
          required: true
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                title:
                  type: string
                source:
                  type: string
                ai_summary:
                  type: string
                published_at:
                  type: string
                  format: date
                expires_at:
                  type: string
                  format: date
      responses:
        200:
          description: 문서 수정 완료
        403:
          description: Admin permission required
    delete:
      tags:
        - admin-documents
      summary: 문서 삭제 (관리자 전용)
      description: 문서를 삭제합니다
      parameters:
        - in: path
          name: doc_id
          schema:
            type: integer
          required: true
      responses:
        200:
          description: 문서 삭제 완료
        403:
          description: Admin permission required
    """

    method_decorators = [admin_required, jwt_required()]

    def put(self, doc_id):
        """문서 수정 (관리자용)"""
        schema = DocumentSchema(partial=True)
        document = Document.query.get_or_404(doc_id)
        document = schema.load(request.json, instance=document)
        db.session.commit()
        return {"message": "문서가 수정되었습니다.", "document": schema.dump(document)}, 200

    def delete(self, doc_id):
        """문서 삭제 (관리자용)"""
        document = Document.query.get_or_404(doc_id)
        db.session.delete(document)
        db.session.commit()
        return {"message": "문서가 삭제되었습니다."}, 200

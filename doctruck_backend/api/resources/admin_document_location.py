"""Admin Document-Location Relation Resource - 공문서-위치 연결 관리

Spring Boot와 비교:
- Resource = @RestController
- admin_required = @PreAuthorize("hasRole('ADMIN')")

Spring 예시:
@RestController
@RequestMapping("/api/v1/admin/documents/{docId}/locations")
@PreAuthorize("hasRole('ADMIN')")
public class DocumentLocationController {
    @PostMapping("/{locationId}")
    public void connectLocation(@PathVariable Long docId, @PathVariable Long locationId) { }

    @DeleteMapping("/{locationId}")
    public void disconnectLocation(@PathVariable Long docId, @PathVariable Long locationId) { }
}
"""

from flask_restful import Resource
from flask_jwt_extended import jwt_required

from doctruck_backend.models import Document, Location, DocumentLocation
from doctruck_backend.extensions import db
from doctruck_backend.api.admin_helpers import admin_required


class AdminDocumentLocationConnect(Resource):
    """공문서-위치 연결 (핵심 기능)

    ---
    post:
      tags:
        - admin-document-location
      summary: 문서-위치 연결 (관리자 전용)
      description: DocumentLocation 연결을 생성합니다 (사용자 맞춤 알림용)
      parameters:
        - in: path
          name: doc_id
          schema:
            type: integer
          required: true
          description: 문서 ID
        - in: path
          name: location_id
          schema:
            type: integer
          required: true
          description: 위치 ID
      responses:
        201:
          description: 연결 완료
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: "공문서와 위치가 연결되었습니다."
                  relation_id:
                    type: integer
        400:
          description: Already connected or invalid IDs
        403:
          description: Admin permission required
        404:
          description: Document or Location not found
    delete:
      tags:
        - admin-document-location
      summary: 문서-위치 연결 해제 (관리자 전용)
      description: DocumentLocation 연결을 삭제합니다
      parameters:
        - in: path
          name: doc_id
          schema:
            type: integer
          required: true
        - in: path
          name: location_id
          schema:
            type: integer
          required: true
      responses:
        200:
          description: 연결 해제 완료
        403:
          description: Admin permission required
        404:
          description: Relation not found
    """

    method_decorators = [admin_required, jwt_required()]

    def post(self, doc_id, location_id):
        """공문서-위치 연결 (관리자용)"""
        # 문서와 위치 존재 확인
        document = Document.query.get_or_404(doc_id)
        location = Location.query.get_or_404(location_id)

        # 이미 연결되어 있는지 확인
        existing = DocumentLocation.query.filter_by(
            doc_id=doc_id,
            location_id=location_id
        ).first()

        if existing:
            return {"message": "이미 연결되어 있습니다."}, 400

        # 새 연결 생성
        relation = DocumentLocation(doc_id=doc_id, location_id=location_id)
        db.session.add(relation)
        db.session.commit()

        return {
            "message": "공문서와 위치가 연결되었습니다.",
            "relation_id": relation.relation_id
        }, 201

    def delete(self, doc_id, location_id):
        """공문서-위치 연결 해제 (관리자용)"""
        relation = DocumentLocation.query.filter_by(
            doc_id=doc_id,
            location_id=location_id
        ).first_or_404()

        db.session.delete(relation)
        db.session.commit()

        return {"message": "공문서와 위치 연결이 해제되었습니다."}, 200


class AdminDocumentLocationList(Resource):
    """문서에 연결된 위치 목록 조회

    ---
    get:
      tags:
        - admin-document-location
      summary: 문서에 연결된 위치 목록 조회 (관리자 전용)
      description: 특정 문서에 연결된 위치 목록을 조회합니다
      parameters:
        - in: path
          name: doc_id
          schema:
            type: integer
          required: true
      responses:
        200:
          description: 연결된 위치 목록
          content:
            application/json:
              schema:
                type: object
                properties:
                  doc_id:
                    type: integer
                  location_ids:
                    type: array
                    items:
                      type: integer
        403:
          description: Admin permission required
        404:
          description: Document not found
    """

    method_decorators = [admin_required, jwt_required()]

    def get(self, doc_id):
        """문서에 연결된 위치 목록 조회 (관리자용)"""
        document = Document.query.get_or_404(doc_id)

        relations = DocumentLocation.query.filter_by(doc_id=doc_id).all()
        location_ids = [r.location_id for r in relations]

        return {
            "doc_id": doc_id,
            "location_ids": location_ids,
            "count": len(location_ids)
        }, 200

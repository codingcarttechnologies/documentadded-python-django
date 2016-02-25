class APIAttached(APIView):
    """
    API for interacting with the documents attached to an application.
    """
    permission_classes = AllowAny,

    @staticmethod
    def get(request, application_pk):
        try:
            application = Application.objects.get(pk=application_pk)
        except ObjectDoesNotExist:
            return Response(status=HTTP_400_BAD_REQUEST)

        if _is_borrower(request):
            borrower = Borrower.objects.for_user(request.user)
            _validate_borrower_for_application(borrower, application)
        elif _is_lender(request):
            from lender.models import Lender
            lender = Lender.objects.for_user(request.user)
            _validate_lender_for_application(lender, application)
        else:
            raise PermissionDenied()

        attachments = application.attachments
        serializer = DocumentApplicationAttacherSerializer(attachments, many=True)

        return Response(serializer.data)


    @staticmethod
    def post(request, application_pk):
        if not _is_borrower(request):
            raise PermissionDenied()

        try:
            application = Application.objects.get(pk=application_pk)
        except ObjectDoesNotExist:
            return Response(status=HTTP_400_BAD_REQUEST)

        #TODO: This is a security hole!
        borrower = Borrower.objects.for_user(request.user)
        _validate_borrower_for_application(borrower, application)
        serializer = DocumentApplicationAttacherSerializer(data=request.data, many=True)

        if serializer.is_valid():
            print ("INSTANCE: {}".format(serializer.instance))
            serializer.save()

            # Now return the current list of attachments for this application
            application = Application.objects.get(pk=application_pk)
            attachments = application.attachments
            serializer = DocumentApplicationAttacherSerializer(attachments, many=True)

            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, application_pk, attachment_pk):
        if not _is_borrower(request):
            raise PermissionDenied()

        try:
            attachment = DocumentApplicationAttacher.objects.get(pk=attachment_pk)
        except ObjectDoesNotExist:
            return Response(status=HTTP_400_BAD_REQUEST)

        borrower = Borrower.objects.for_user(request.user)
        application = attachment.application
        _validate_borrower_for_application(borrower, application)

        attachment.delete()

        # Now return the current attachments for this application
        application = Application.objects.get(pk=application_pk)
        attachments = application.attachments
        serializer = DocumentApplicationAttacherSerializer(attachments, many=True)
        return Response(serializer.data)


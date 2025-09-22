def interpret(line_type, attrs):
    """
    line_type: 'life'|'heart'|'head'|'fate'
    attrs: dict {'length_cls','slope_cls','curv_cls','breaks_cls'}
    """
    s = []

    # ---- Các câu bạn yêu cầu ----
    # 1. Sức sống, độ lượng, hào phóng (life dài+sâu ~ ở đây dùng length long & breaks none)
    if line_type=="life" and attrs.get("length_cls")=="long" and attrs.get("breaks_cls")=="none":
        s.append("Là người có sức sống, sức khỏe dồi dào, độ lượng, hào phóng")

    # 2. Cởi mở, hòa đồng (heart hướng lên + cong nhẹ)
    if line_type=="heart" and attrs.get("slope_cls")=="up" and attrs.get("curv_cls")!="high":
        s.append("Tính tình rộng rãi, cởi mở, hòa đồng")

    # 3. Ước mơ, tham vọng, tự tin (fate rõ hoặc life rất dài)
    if (line_type=="fate" and attrs.get("breaks_cls")!="many") or \
       (line_type=="life" and attrs.get("length_cls")=="long"):
        s.append("Có nhiều ước mơ, tham vọng, tự tin")

    # 4. Thần kinh vững vàng, sáng suốt (head ít gãy, cong thấp)
    if line_type=="head" and attrs.get("breaks_cls")=="none" and attrs.get("curv_cls")!="high":
        s.append("Thần kinh vững vàng, sáng suốt, ít bệnh tật")

    # 5. Tuổi nhỏ dựa vào cha mẹ, kém phát triển (fate vắng/đứt, life ngắn)
    if (line_type=="fate" and attrs.get("breaks_cls")!="none") or \
       (line_type=="life" and attrs.get("length_cls")=="short"):
        s.append("Thời nhỏ sống dựa vào cha mẹ nhiều, hơi kém phát triển")

    # 6. Thiếu nghị lực, nhẹ dạ (head gãy hoặc cong mạnh)
    if line_type=="head" and (attrs.get("breaks_cls")!="none" or attrs.get("curv_cls")=="high"):
        s.append("Thiếu nghị lực, hơi nhẹ dạ")

    # 7. Nhân từ, tận tụy (heart khá thẳng/hướng lên)
    if line_type=="heart" and attrs.get("slope_cls") in ["flat","up"]:
        s.append("Có lòng nhân tử, hảo tâm, tận tụy hết lòng vì gia đình, bè bạn")

    # 8. Ít nhiệt tình, ưa vật chất (heart nông ~ ở đây dùng 'down' hoặc cong thấp nhưng nhiều breaks)
    if line_type=="heart" and (attrs.get("slope_cls")=="down" or attrs.get("breaks_cls")!="none"):
        s.append("Ít nhiệt tình, ưa vật chất")

    # 9. Cuộc đời khá dễ dàng (fate không có breaks; life không đứt)
    if (line_type=="fate" and attrs.get("breaks_cls")=="none") or \
       (line_type=="life" and attrs.get("breaks_cls")=="none"):
        s.append("Cuộc đời khá dễ dàng, phẳng lặng")

    # 10. Bấp bênh, nhiều thay đổi (fate nhiều breaks)
    if line_type=="fate" and attrs.get("breaks_cls")=="many":
        s.append("Cuộc đời bấp bênh, nhiều thay đổi")

    # loại trùng
    out=[]
    for t in s:
        if t not in out: out.append(t)
    return out

def img_gen(left_camera, right_camera):
    while True:
        l_ret, l_frame = left_camera.read()
        r_ret, r_frame = right_camera.read()
        if l_ret and r_ret:
            yield l_frame, r_frame
        else:
            break

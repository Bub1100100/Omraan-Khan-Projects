videoFile = "test_vid.mp4"; %Video File Name

disp("Starting Read") %Reading video Data
videoObj = VideoReader(videoFile);
Frame_data =video_to_data(videoObj, false, 20);
Frame_rate = videoObj.FrameRate;

%disp('Converting to YCBCR')
%modified_Frame_data = convert_to_YCBCR(Frame_data);

percent = 20;
disp('Foviating')
modified_Frame_data=foviate2(Frame_data, 860, 490, 5);

%disp('Converting to RGB')
%modified_Frame_data = convert_to_RGB(modified_Frame_data);


disp('Starting Write') %Writing modified data
output_file = "Foviate-Test";
write_video(modified_Frame_data, output_file, Frame_rate);
disp("DONE")




function videoData = video_to_data(videoObj, play, short)
    % Create a VideoReader object
    
    % Preallocate a matrix to store video frames
    numFrames = floor(videoObj.Duration * videoObj.FrameRate);
    frameHeight = videoObj.Height;
    frameWidth = videoObj.Width;
    videoData = zeros(frameHeight, frameWidth, 3, short, 'uint8');
    
    % Read video frames into the matrix
    for k = 1:short
        if hasFrame(videoObj)
            videoData(:, :, :, k) = readFrame(videoObj);
        end
    end
    
    % Play back the video if playback enabled
    if(play == true)
        figure;
        for k = 1:short
            imshow(videoData(:, :, :, k));
            pause(1/videoObj.FrameRate);
        end
    end

end

function write_video(videoData, outputFile, frameRate)
    % Create a VideoWriter object
    writerObj = VideoWriter(outputFile, 'MPEG-4');
    writerObj.FrameRate = frameRate;
    open(writerObj);
    
    % Write each frame to the video file
    numFrames = size(videoData, 4);
    for k = 1:numFrames
        writeVideo(writerObj, squeeze(videoData(:, :, :, k)));
    end
    
    % Close the VideoWriter object
    close(writerObj);
end

function modified_data = convert_to_YCBCR(videoData)
    frameHeight = size(videoData, 1);
    frameWidth  = size(videoData, 2);
    numFrames = size(videoData, 4);

    modified_data = zeros(frameHeight, frameWidth, 3, numFrames, 'uint8');
    
    for k = 1:numFrames
       %convert to YCBCR
        modified_data(:, :, :, k) = rgb2ycbcr(videoData(:, :, :, k));
    end
end



function modified_data = convert_to_RGB(videoData)
    frameHeight = size(videoData, 1);
    frameWidth  = size(videoData, 2);
    numFrames = size(videoData, 4);

    modified_data = zeros(frameHeight, frameWidth, 3, numFrames, 'uint8');
    
    for k = 1:numFrames
        %Convert to RGB
        modified_data(:, :, :, k) = ycbcr2rgb(videoData(:, :, :, k));
    end
end

function modified_data = remove_edge_color(videoData, H_border, V_border, drop_factor)
    frameHeight = size(videoData, 1);
    frameWidth  = size(videoData, 2);
    numFrames = size(videoData, 4);

    modified_data = videoData;

    for k = 1:numFrames
        %remove edge cb/cr
        if(frameWidth ~= H_border)
            modified_data(1:frameHeight, 1:drop_factor:H_border, 2:3, k) = 128; %Left Edge
            modified_data(1:frameHeight, frameWidth-H_border:drop_factor:frameWidth, 2:3, k) = 128; %Right Edge
        else
            modified_data(1:frameHeight, 1:drop_factor:frameWidth, 2:3, k) = 128; %Left Edge
        end
        
        if(frameHeight ~= V_border)
        modified_data(1:drop_factor:V_border, H_border:frameWidth-H_border, 2:3, k) = 128; %Top Edge
        modified_data(frameHeight-V_border:drop_factor:frameHeight, H_border:frameWidth-H_border, 2:3, k) = 128; %Bottom Edge
        else
            modified_data(1:drop_factor:frameHeight, 1:frameWidth, 2:3, k) = 128; %Left Edge
        end

        %remove edge cr
        %modified_data(1:frameHeight, 1:H_border, 3, k) = 0; %Left Edge
        %modified_data(1:frameHeight, frameWidth-H_border:frameWidth, 3, k) = 0; %Right Edge
        %modified_data(1:V_border, 1:frameWidth, 3, k) = 0; %Top Edge
        %modified_data(frameHeight-V_border:frameHeight, 1:frameWidth, 3, k) = 0; %Bottom Edge
    end
end


function modified_data = foviate2(videoData, H_border, V_border, comp_ratio)
        numFrames = size(videoData, 4);
        Width = size(videoData, 2);
        Height = size(videoData, 1);
        

        Left_Width = H_border;
        Middle_Width = Width-(2*H_border);
        Right_Width = H_border;

        Top_Height = V_border;
        Middle_Height = Height - (2*V_border);
        Bottom_Height = V_border;
        
            
        New_Width = cast(Middle_Width + Left_Width/comp_ratio + Right_Width/comp_ratio,"int64");
        New_Height = cast(Middle_Height + Top_Height/comp_ratio + Bottom_Height/comp_ratio,"int64");

        modified_data = zeros(New_Height, New_Width, 3, numFrames, 'uint8');

   
        for k = 1:numFrames
            Frame_data = videoData(:,:,:,k);
             
            TL_data = Frame_data(1:Top_Height, 1:Left_Width, :);
            TM_data = Frame_data(1:Top_Height, Left_Width+1:Left_Width+Middle_Width, :);
            TR_data = Frame_data(1:Top_Height, Width-Right_Width+1:Width, :);
                
            ML_data = Frame_data(Top_Height+1:Top_Height+Middle_Height, 1:Left_Width, :);
            MM_data = Frame_data(Top_Height+1:Top_Height+Middle_Height, Left_Width+1:Left_Width+Middle_Width, :);
            MR_data = Frame_data(Top_Height+1:Top_Height+Middle_Height, Width-Right_Width+1:Width, :);

            BL_data = Frame_data(Height-Bottom_Height+1:Height, 1:Left_Width, :);
            BM_data = Frame_data(Height-Bottom_Height+1:Height, Left_Width+1:Left_Width+Middle_Width, :);
            BR_data = Frame_data(Height-Bottom_Height+1:Height, Width-Right_Width+1:Width, :);
             

            TL_data =  imresize(TL_data, [size(TL_data,1)/comp_ratio, size(TL_data,2)/comp_ratio]);
            TM_data =  imresize(TM_data, [size(TM_data,1)/comp_ratio, size(TM_data,2)]);
            TR_data =  imresize(TR_data, [size(TR_data,1)/comp_ratio, size(TR_data,2)/comp_ratio]);

            ML_data =  imresize(ML_data, [size(ML_data,1), size(ML_data,2)/comp_ratio]);
            MM_data =  imresize(MM_data, 1);
            MR_data =  imresize(MR_data, [size(MR_data,1), size(MR_data,2)/comp_ratio]);

            BL_data =  imresize(BL_data, [size(BL_data,1)/comp_ratio, size(BL_data,2)/comp_ratio]);
            BM_data =  imresize(BM_data, [size(BM_data,1)/comp_ratio, size(BM_data,2)]);
            BR_data =  imresize(BR_data, [size(BR_data,1)/comp_ratio, size(BR_data,2)/comp_ratio]);


            Top_data = cat(2, TL_data, TM_data, TR_data);
            Middle_data = cat(2, ML_data, MM_data, MR_data);
            Bottom_data = cat(2, BL_data, BM_data, BR_data);

            modified_frame = cat(1, Top_data, Middle_data, Bottom_data);

            modified_data(:,:,:,k) = modified_frame;
        end


end

function modified_data = foviate(videoData, percent, comp_ratio)
        numFrames = size(videoData, 4);

        Width = size(videoData, 2);
        Height = size(videoData, 1);

        H_border = cast(Width*percent/100, "int64");
        V_border = cast(Height*percent/100, "int64");
        

        Center_width = cast(Width - 2*H_border, "int64");
        Center_height = cast(Height - 2*V_border, "int64");

        modified_width = Center_width + (2*H_border)/comp_ratio;
        modified_height = Center_height + (2*V_border)/comp_ratio;

        
        modified_data = zeros(modified_height, modified_width, 3, numFrames, 'uint8');

        Left_box = [1,V_border+1, H_border-1, Height-(2*V_border)-1];
        Right_box = [Width-H_border,V_border+1, H_border-1, Height-(2*V_border)-1];
        Top_box = [1,1,Width-1, V_border-1];
        Bottom_box = [1, (Height-V_border) ,Width-1, V_border-1];
        Center_box = [H_border+1, V_border+1, Width-(2*H_border)-1, Height-(2*V_border)-1];
        
       

        for k = 1:numFrames
            frameData = videoData(:,:,:,k);

            L_data = imcrop(frameData, Left_box);
            R_data = imcrop(frameData, Right_box);
            T_data = imcrop(frameData, Top_box);
            B_data = imcrop(frameData, Bottom_box);
            C_data = imcrop(frameData, Center_box);
            
            
            M_L_data = imresize(L_data, [Height-2*V_border,H_border/comp_ratio]);
            M_R_data = imresize(R_data, [Height-2*V_border,H_border/comp_ratio]);
            M_T_data = imresize(T_data, [V_border/comp_ratio,Width-(2*H_border)+2*(H_border/comp_ratio)]);
            M_B_data = imresize(B_data, [V_border/comp_ratio,Width-(2*H_border)+2*(H_border/comp_ratio)]);
            
           
            
            %modified_frame = cat(2, L_data, C_data, R_data);
            %modified_frame = cat(1, T_data, modified_frame, B_data);

            modified_frame = cat(2, M_L_data, C_data, M_R_data);
            modified_frame = cat(1, M_T_data, modified_frame, M_B_data);


         
            modified_data(:,:,:,k) = modified_frame;

        end
end


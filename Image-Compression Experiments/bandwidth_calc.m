clc
clearvars
% Intitalize compression ratio vals
comp_ratio = 1:50;
constant = ones(50);
%Taking user input for screen vars
resoloution_h = input("Please enter the resolution height: ");
resoloution_w = input("Please enter the resolution width: ");
bits_per_pixel = input("Enter bits per pixel: ");
num_of_screens = input("Enter number of screens: ");

%Taking user inputs for time constraints
frame_rate = input("Enter the frame rate: ");
latency = input("Enter the target latency: ");

%Calculations:
latency_rate =  1000 / latency;
bits_per_frame = (resoloution_w * resoloution_h* bits_per_pixel * num_of_screens) ./comp_ratio;
peak_bandwidth = max(bits_per_frame * frame_rate, bits_per_frame * latency_rate) ./1000000;
average_bandwidth = bits_per_frame * frame_rate/1000000;


%Wifi Standard constants
wifi_8 = 100000 * constant;
wifi_7 = 23059 * constant;
wifi_6 = 9608 * constant;
wifi_5 = 6933 * constant;

%plotting
figure; 
plot(peak_bandwidth); 
hold on;
plot(average_bandwidth);
hold on;
plot(wifi_7);
hold on;
plot(wifi_6);
hold on;
plot(wifi_5);
hold off;
legend('peak_bandwidth', 'avg_bandwidth', 'wifi_7', 'wifi_6', 'wifi_5');
xlabel('Compression Ratio'); % Label the x-axis
ylabel('Bandwidth Mbps'); % Label the y-axis
title('Multiple Arrays vs. Index'); % Add a title
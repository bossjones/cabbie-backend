BEGIN { FS = ";" } 

$2 ~/WebSessionLocation/ { 

#printf ("[1]%s [2]%s [3]%s\n", $1, $2, $3)

# 특수문자 제거 및 날자구분
	split($1, Date_Temp, " ")
	split(Date_Temp[1], Date, "")
	split(Date_Temp[2], Time, ",")

# 기사 ID 추출
	split($2, D_Id_Temp,"(");
	split(D_Id_Temp[2], D_Id,")");


# 위경도 추출 
	split($3, var, " ") ; 
	split(var[4], location_temp, "[");
	split(location_temp[2], location_temp_second, "]");
	split(location_temp_second[1], location, ",");


# 실제 사용 변수
# 날자 : Date[2]
# 시간 : Time[1]
# 기사 : D_Id[1]
# 위도 : location[2]
# 경도 : location[1]

	printf "%s\t%s\t%s\t%s\t%s\n", Date[2], Time[1], D_Id[1], location[2] ,location[1];

}





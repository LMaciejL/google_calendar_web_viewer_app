$(document).ready(function () {
    updateMeetings();
    setInterval(updateMeetings, 60000);  // Odświeżaj co 60 sekund
});

function updateMeetings() {
    $.get("/api/today_meetings", function (data) {
        const meetingList = $(".meeting-list");
        meetingList.empty();

        if (data.meetings.length === 0) {
            meetingList.append("<li class='meeting-item'><div><span class='meeting-title'>Brak dzisiejszych spotkań.</span></div></li>");
        } else {
            data.meetings.forEach(function (meeting) {
                const meetingItem = `<li class='meeting-item'><div>
					<span class='meeting-title'>${meeting.title}</span><p class='meeting-time'>${meeting.timeStart} - ${meeting.timeEnd}</p></div></li>`;
                meetingList.append(meetingItem);
            });
        }
    });
}

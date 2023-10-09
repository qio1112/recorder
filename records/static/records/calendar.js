const calendarBody = document.getElementById('calendar-body');
const monthYearElement = document.getElementById('month-year');

function generateCalendar(year, month) {
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const firstDay = new Date(year, month, 1).getDay();
  const lastDay = new Date(year, month, daysInMonth).getDay();

  const dates = [];

  for (let i = 1; i <= daysInMonth; i++) {
    dates.push(i);
  }

  let calendarHTML = '';
  let index = 0;

  calendarHTML += '<tr>';

  for (let i = 0; i < firstDay; i++) {
    calendarHTML += '<td></td>';
  }

  for (let i = 1; i <= daysInMonth; i++) {
    calendarHTML += `<td onclick="selectDate(${i})">${dates[index]}</td>`;
    index++;
    if ((i + firstDay) % 7 === 0) {
      calendarHTML += '</tr><tr>';
    }
  }

  for (let i = lastDay + 1; i < 7; i++) {
    calendarHTML += '<td></td>';
  }

  calendarHTML += '</tr>';

  calendarBody.innerHTML = calendarHTML;
}

function updateCalendar(year, month) {
  const months = [
    'January', 'February', 'March', 'April',
    'May', 'June', 'July', 'August',
    'September', 'October', 'November', 'December'
  ];

  monthYearElement.textContent = months[month] + ' ' + year;
  generateCalendar(year, month);
}

function nextMonth() {
  const currentMonth = new Date().getMonth();
  const currentYear = new Date().getFullYear();
  const nextMonth = (currentMonth + 1) % 12;
  const year = currentMonth === 11 ? currentYear + 1 : currentYear;
  updateCalendar(year, nextMonth);
}

function previousMonth() {
  const currentMonth = new Date().getMonth();
  const currentYear = new Date().getFullYear();
  const previousMonth = (currentMonth - 1 + 12) % 12;
  const year = currentMonth === 0 ? currentYear - 1 : currentYear;
  updateCalendar(year, previousMonth);
}

function selectDate(day) {
  const selectedDate = new Date(monthYearElement.textContent + ' ' + day);
  const tdElements = document.getElementsByTagName('td');

  // Reset previously selected dates
  for (let i = 0; i < tdElements.length; i++) {
    tdElements[i].classList.remove('selected');
  }

  // Mark the selected date
  event.target.classList.add('selected');

  // Use the selected date (in this example, we're just logging it)
  console.log('Selected date:', selectedDate.toDateString());
}

// Initialize the calendar
const currentMonth = new Date().getMonth();
const currentYear = new Date().getFullYear();
updateCalendar(currentYear, currentMonth);

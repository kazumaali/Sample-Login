const loginBtn = document.getElementById("loginBtn");
const emailLogInput = document.getElementById("emailLogInput");
const message = document.getElementById("message");
const passwordLogInput = document.getElementById("passwordLogInput");
const loginForm = document.getElementById("loginForm");
const signupForm = document.getElementById("signupForm");
const nameInput = document.getElementById("nameInput");
const emailInput = document.getElementById("emailInput");
const passwordInput = document.getElementById("passwordInput");
const repeatPasswordInput = document.getElementById("repeatPasswordInput");
const verificationForm = document.getElementById("verificationForm");
const verificationInput = document.getElementById("verificationInput");
const loginRedirectBtn = document.getElementById("loginRedirectBtn")
const signupRedirectBtn = document.getElementById("signupRedirectBtn");
const resendCodeBtn = document.getElementById("resendCodeBtn");
const forgotPasswordBtn = document.getElementById("forgotPasswordBtn");
const forgotPasswordForm = document.getElementById("forgotPasswordForm");
const forgotPasswordInput = document.getElementById("forgotPasswordInput");  
const changePasswordForm = document.getElementById("changePasswordForm");
const changePasswordInput = document.getElementById("changePasswordInput");
const resendForgotPasswordCodeBtn = document.getElementById("resendForgotPasswordCodeBtn");

// Form switching
signupRedirectBtn.addEventListener("click", function(e) {
    e.preventDefault();
    signupForm.style.display = 'block';
    loginForm.style.display = 'none';
    message.style.display = 'none';
});

loginRedirectBtn.addEventListener ("click", function(e) {
    e.preventDefault();
    signupForm.style.display = 'none';
    loginForm.style.display = 'block';
    message.style.display = 'none';
});

// Login functionality
loginForm.addEventListener("submit", function(e) {
    e.preventDefault();
    
    const users = JSON.parse(localStorage.getItem('users')) || [];
    const user = users.find(u => u.email === emailLogInput.value);
    
    if(!user){
        console.error("User Does Not Exist!");
        message.style.display = 'block';
        message.textContent = "لا وجود لهذا المستخدم!"
        message.style.backgroundColor = "red";
        message.style.color = "white";
        return;
    }
    
    if(user.password !== passwordLogInput.value){
        console.error('Incorrect Password!');
        message.style.display = 'block';
        message.textContent = 'كلمة مرور خاطئة!';
        message.style.backgroundColor = 'red';
        message.style.color = 'white';
        return;
    };
    
    console.log('Login Successfully');
    message.style.display = 'block';
    message.textContent = 'تم تسجيل الدخول بنجاح';
    message.style.backgroundColor = 'green';
    message.style.color = 'white';
    
    sessionStorage.setItem('currentUser', JSON.stringify(user));
    
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 2000);
});

// Signup functionality
signupForm.addEventListener("submit", function(e) {
    e.preventDefault();
    
    let hasError = false;
    
    if (!/^[A-Za-z0-9_]{3,16}$/.test(nameInput.value)) {
        console.error("Invalid Username!");
        hasError = true;
        message.style.display = 'block';
        message.textContent = "صيغة خاطئة! على إسم المستخدم أن يحتوي على حروف لاتينية، أو الأرقام من 1-9 ، أو _، أو $. وأن يحتوي بين 3 إلى 16 عنصرا."
        message.style.backgroundColor = "red";
        message.style.color = "white";
    }
    
    if(!emailInput.checkValidity()){
        console.error("Invalid Email Address!");
        hasError = true;
        message.style.display = 'block';
        message.textContent = "عنوان بريد إلكترونيٍّ خاطئ!"
        message.style.backgroundColor = "red";
        message.style.color = "white";
    }
    
    if(!passwordInput.checkValidity()){
        console.error("Invalid Password Shape!");
        hasError = true;
        message.style.display = 'block';
        message.textContent = "على كلمة المرور أن تحتوي على الحروف اللاتينية، أو الأرقام 1-9، أو $. وأن يحتوي على الأقل على 6 عناصر."
        message.style.backgroundColor = "red";
        message.style.color = "white";
    }
    
    if(passwordInput.value !== repeatPasswordInput.value){
        console.error("Passwords Do Not Match!");
        hasError = true;
        message.style.display = 'block';
        message.textContent = "كلمتا المرور ليستا متطابقتين!"
        message.style.backgroundColor = "red";
        message.style.color = "white";
    }

    // Check if user already exists
    const existingUsers = JSON.parse(localStorage.getItem('users')) || [];
    const userExists = existingUsers.some(user => user.email === emailInput.value);
    if(userExists){
        console.error('User Already Exists!');
        message.style.display = 'block';
        message.textContent = 'المستخدم موجود بالفعل!';
        message.style.backgroundColor = 'red';
        message.style.color = 'white';
        return;
    }

    if(!hasError){
        // Store temporary user data
        const tempUserData = {
            name: nameInput.value,
            email: emailInput.value,
            password: passwordInput.value
        };
        sessionStorage.setItem('tempUserData', JSON.stringify(tempUserData));
        
        // Generate and send verification code
        sendVerificationCode(emailInput.value, 'signup');
        
        verificationForm.style.display = 'block';
        signupForm.style.display = 'none';
        message.style.display = 'none';
    }
});

// Verification functionality
verificationForm.addEventListener("submit", function(e){
    e.preventDefault();
    
    const storedCode = sessionStorage.getItem('verificationCode');
    
    if(verificationInput.value !== storedCode){
        console.error('Invalid Verification Code!');
        message.style.display = 'block';
        message.textContent = 'رمز تأكيدٍ خاطئ!';
        message.style.backgroundColor = 'red';
        message.style.color = 'white';
    } else {
        const userData = JSON.parse(sessionStorage.getItem('tempUserData'));
        
        const existingUsers = JSON.parse(localStorage.getItem('users')) || [];
        existingUsers.push(userData);
        
        localStorage.setItem('users', JSON.stringify(existingUsers));
        
        // Clean up
        sessionStorage.removeItem('verificationCode');
        sessionStorage.removeItem('tempUserData');
        
        nameInput.value = '';
        emailInput.value = '';
        passwordInput.value = '';
        repeatPasswordInput.value = '';
        verificationInput.value = '';
        
        console.log('Account Created Successfully🎉');
        message.style.display = 'block';
        message.textContent = 'تم إنشاء الحساب بنجاح🎉';
        message.style.backgroundColor = 'green';
        message.style.color = 'white';
        
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 2000);
    }
});

// Resend code for signup
resendCodeBtn.addEventListener("click", function(e){
    e.preventDefault();
    const tempUserData = JSON.parse(sessionStorage.getItem('tempUserData'));
    if (tempUserData && tempUserData.email) {
        sendVerificationCode(tempUserData.email, 'signup');
    }
});

// Forgot password functionality
forgotPasswordBtn.addEventListener("click", function(e){
    e.preventDefault();
    
    const email = emailLogInput.value;
    if (!email) {
        message.style.display = 'block';
        message.textContent = 'الرجاء إدخال البريد الإلكتروني أولاً!';
        message.style.backgroundColor = 'red';
        message.style.color = 'white';
        return;
    }
    
    // Check if user exists
    const users = JSON.parse(localStorage.getItem('users')) || [];
    const user = users.find(u => u.email === email);
    
    if(!user){
        message.style.display = 'block';
        message.textContent = "لا وجود لهذا المستخدم!"
        message.style.backgroundColor = "red";
        message.style.color = "white";
        return;
    }
    
    sessionStorage.setItem('resetPasswordEmail', email);
    sendVerificationCode2(email, 'forgotPassword');
    
    forgotPasswordForm.style.display = 'block';
    loginForm.style.display = 'none';
    message.style.display = 'none';
});

// Resend code for forgot password
resendForgotPasswordCodeBtn.addEventListener("click", function(e){
    e.preventDefault();
    const email = sessionStorage.getItem('resetPasswordEmail');
    if (email) {
        sendVerificationCode2(email, 'forgotPassword');
    }
});

// Forgot password verification
forgotPasswordForm.addEventListener("submit", function(e) {
    e.preventDefault();
    
    const storedCode = sessionStorage.getItem('verificationCode');
    
    if(forgotPasswordInput.value !== storedCode) {
        console.error("Invalid Verification Code!");
        message.style.display = 'block';
        message.textContent = "رمز تأكيد خاطئ!";
        message.style.backgroundColor = "red";
        message.style.color = "white";
        return;
    }
    
    console.log("Redirected to changePasswordForm");
    forgotPasswordForm.style.display = 'none';
    changePasswordForm.style.display = 'block';
    message.style.display = 'none';
});

// Change password functionality
changePasswordForm.addEventListener("submit", function(e){
    e.preventDefault();
    
    if(!changePasswordInput.checkValidity()){
        console.error("Invalid Password Shape!");
        message.style.display = 'block';
        message.textContent = "على كلمة المرور أن تحتوي على الحروف اللاتينية، أو الأرقام 1-9، أو $. وأن يحتوي على الأقل على 6 عناصر."
        message.style.backgroundColor = "red";
        message.style.color = "white";
        return;
    }
    
    const userEmail = sessionStorage.getItem('resetPasswordEmail');
    
    if (!userEmail) {
        console.error("No user email found for password reset!");
        message.style.display = 'block';
        message.textContent = "خطأ في عملية إعادة تعيين كلمة المرور!";
        message.style.backgroundColor = "red";
        message.style.color = "white";
        return;
    }
    
    const users = JSON.parse(localStorage.getItem('users')) || [];
    const userIndex = users.findIndex(user => user.email === userEmail);
    
    if (userIndex === -1) {
        console.error("User not found!");
        message.style.display = 'block';
        message.textContent = "المستخدم غير موجود!";
        message.style.backgroundColor = "red";
        message.style.color = "white";
        return;
    }
    
    users[userIndex].password = changePasswordInput.value;
    localStorage.setItem('users', JSON.stringify(users));
    
    sessionStorage.removeItem('verificationCode');
    sessionStorage.removeItem('resetPasswordEmail');
    
    changePasswordInput.value = '';
    
    console.log("Password changed successfully!");
    message.style.display = 'block';
    message.textContent = "تم تغيير كلمة المرور بنجاح!";
    message.style.backgroundColor = "green";
    message.style.color = "white";
    
    setTimeout(() => {
        changePasswordForm.style.display = 'none';
        loginForm.style.display = 'block';
        message.style.display = 'block';
    }, 2000);
});

// Helper function to send verification code
function sendVerificationCode(email, type) {
    const verificationCode = Math.floor(100000 + Math.random() * 900000);
    sessionStorage.setItem('verificationCode', verificationCode);
    
    const templateParams = {
        verification_code: verificationCode,
        to_email: emailInput.value,
        username: nameInput.value
    };
    
    emailjs.send("service_0ias34f", "template_z6biz19", templateParams)
    .then(() => {
        alert("تم إرسال رمز التأكيد إليك. رجاءاً تفقد بريدك الإلكتروني.");
    })
    .catch((error) => {
        console.error(error);
        alert('فشل الإرسال! رجاءاً إضغط على "إعادة الإرسال".');
    });
}

function sendVerificationCode2(email, type) {
    const verificationCode = Math.floor(100000 + Math.random() * 900000);
    sessionStorage.setItem('verificationCode', verificationCode);
    
    const templateParams = {
        verification_code: verificationCode,
        to_email: email,
        username: user.name
    };
    
    emailjs.send("service_0ias34f", "template_z6biz19", templateParams)
    .then(() => {
        alert("تم إرسال رمز التأكيد إليك. رجاءاً تفقد بريدك الإلكتروني.");
    })
    .catch((error) => {
        console.error(error);
        alert('فشل الإرسال! رجاءاً إضغط على "إعادة الإرسال".');
    });
}
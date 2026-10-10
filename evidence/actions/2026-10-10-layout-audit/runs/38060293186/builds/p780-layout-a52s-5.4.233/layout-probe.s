	.text
	.file	"p780-layout-probe.c"
	.globl	main                    // -- Begin function main
	.p2align	2
	.type	main,@function
main:                                   // @main
.Lmain$local:
// %bb.0:
	//APP
	
.ascii "->(test_ti_thread_flag(((struct thread_info *)get_current()), 22) ? ((((0x100000000UL))) - ((1UL) << 12)) : ((((1UL))) << vabits_actual)) 4096 sizeof(struct task_struct)"
	//NO_APP
	//APP
	
.ascii "->TASK_PID 1664 offsetof(struct task_struct, pid)"
	//NO_APP
	//APP
	
.ascii "->TASK_COMM 2120 offsetof(struct task_struct, comm)"
	//NO_APP
	//APP
	
.ascii "->TASK_CRED 2104 offsetof(struct task_struct, cred)"
	//NO_APP
	//APP
	
.ascii "->TASK_REAL_CRED 2096 offsetof(struct task_struct, real_cred)"
	//NO_APP
	//APP
	
.ascii "->TASK_PI_LOCK 2316 offsetof(struct task_struct, pi_lock)"
	//NO_APP
	//APP
	
.ascii "->TASK_PI_BLOCKED_ON 2352 offsetof(struct task_struct, pi_blocked_on)"
	//NO_APP
	//APP
	
.ascii "->CRED_SIZE 168 sizeof(struct cred)"
	//NO_APP
	//APP
	
.ascii "->CRED_USAGE 0 offsetof(struct cred, usage)"
	//NO_APP
	//APP
	
.ascii "->CRED_UID 4 offsetof(struct cred, uid)"
	//NO_APP
	//APP
	
.ascii "->CRED_SECURITY 120 offsetof(struct cred, security)"
	//NO_APP
	//APP
	
.ascii "->REFCOUNT_SIZE 4 sizeof(refcount_t)"
	//NO_APP
	//APP
	
.ascii "->WAITER_SIZE 80 sizeof(struct rt_mutex_waiter)"
	//NO_APP
	//APP
	
.ascii "->WAITER_TASK 48 offsetof(struct rt_mutex_waiter, task)"
	//NO_APP
	//APP
	
.ascii "->WAITER_LOCK 56 offsetof(struct rt_mutex_waiter, lock)"
	//NO_APP
	//APP
	
.ascii "->WAITER_TREE 0 offsetof(struct rt_mutex_waiter, tree_entry)"
	//NO_APP
	//APP
	
.ascii "->RTMUTEX_SIZE 32 sizeof(struct rt_mutex)"
	//NO_APP
	//APP
	
.ascii "->MM_SIZE 912 sizeof(struct mm_struct)"
	//NO_APP
	//APP
	
.ascii "->MM_PGD 72 offsetof(struct mm_struct, pgd)"
	//NO_APP
	//APP
	
.ascii "->PAGE_SIZEOF 64 sizeof(struct page)"
	//NO_APP
	//APP
	
.ascii "->PAGE_FLAGS 0 offsetof(struct page, flags)"
	//NO_APP
	//APP
	
.ascii "->PAGE_SLAB_CACHE 24 offsetof(struct page, slab_cache)"
	//NO_APP
	//APP
	
.ascii "->FILE_SIZE 272 sizeof(struct file)"
	//NO_APP
	//APP
	
.ascii "->FILE_F_OP 40 offsetof(struct file, f_op)"
	//NO_APP
	//APP
	
.ascii "->FILE_F_COUNT 56 offsetof(struct file, f_count)"
	//NO_APP
	//APP
	
.ascii "->FOPS_SIZE 288 sizeof(struct file_operations)"
	//NO_APP
	//APP
	
.ascii "->FOPS_IOCTL 80 offsetof(struct file_operations, unlocked_ioctl)"
	//NO_APP
	//APP
	
.ascii "->PIPE_INFO_SIZE 136 sizeof(struct pipe_inode_info)"
	//NO_APP
	//APP
	
.ascii "->PIPE_INFO_BUFS 120 offsetof(struct pipe_inode_info, bufs)"
	//NO_APP
	//APP
	
.ascii "->PIPE_BUFFER_SIZEOF 40 sizeof(struct pipe_buffer)"
	//NO_APP
	//APP
	
.ascii "->PIPE_BUFFER_PAGE 0 offsetof(struct pipe_buffer, page)"
	//NO_APP
	//APP
	
.ascii "->PIPE_BUFFER_OPS 16 offsetof(struct pipe_buffer, ops)"
	//NO_APP
	mov	w0, wzr
	ret
.Lfunc_end0:
	.size	main, .Lfunc_end0-main
                                        // -- End function
	.ident	"Android (6877366 based on r383902b1) clang version 11.0.2 (https://android.googlesource.com/toolchain/llvm-project b397f81060ce6d701042b782172ed13bee898b79)"
	.section	".note.GNU-stack","",@progbits

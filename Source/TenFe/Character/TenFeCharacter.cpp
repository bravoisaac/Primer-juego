#include "Character/TenFeCharacter.h"

#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TenFeEquipmentComponent.h"
#include "Components/TenFeStatsComponent.h"
#include "Engine/DamageEvents.h"
#include "Engine/OverlapResult.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"
#include "UI/TenFeEquipmentMenuWidget.h"
#include "UI/TenFeHUDWidget.h"

ATenFeCharacter::ATenFeCharacter()
{
    PrimaryActorTick.bCanEverTick = true;

    GetCapsuleComponent()->InitCapsuleSize(42.0f, 92.0f);
    bUseControllerRotationPitch = false;
    bUseControllerRotationYaw = false;
    bUseControllerRotationRoll = false;

    GetCharacterMovement()->bOrientRotationToMovement = true;
    GetCharacterMovement()->RotationRate = FRotator(0.0f, 520.0f, 0.0f);
    GetCharacterMovement()->MaxWalkSpeed = BaseWalkSpeed;
    GetCharacterMovement()->JumpZVelocity = 520.0f;
    GetCharacterMovement()->AirControl = 0.3f;

    CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
    CameraBoom->SetupAttachment(RootComponent);
    CameraBoom->TargetArmLength = 360.0f;
    CameraBoom->SetRelativeLocation(FVector(0.0f, 0.0f, 70.0f));
    CameraBoom->bUsePawnControlRotation = true;

    FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
    FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
    FollowCamera->bUsePawnControlRotation = false;

    BodyVisual = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BodyVisual"));
    BodyVisual->SetupAttachment(RootComponent);
    BodyVisual->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    BodyVisual->SetRelativeScale3D(FVector(0.48f, 0.38f, 1.35f));
    BodyVisual->SetRelativeLocation(FVector(0.0f, 0.0f, -8.0f));

    WeaponVisual = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("WeaponVisual"));
    WeaponVisual->SetupAttachment(RootComponent);
    WeaponVisual->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    WeaponVisual->SetRelativeLocation(FVector(24.0f, 42.0f, 5.0f));
    WeaponVisual->SetRelativeRotation(FRotator(0.0f, 0.0f, 90.0f));

    static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeAsset(TEXT("/Engine/BasicShapes/Cube.Cube"));
    if (CubeAsset.Succeeded())
    {
        BodyVisual->SetStaticMesh(CubeAsset.Object);
        WeaponVisual->SetStaticMesh(CubeAsset.Object);
    }

    Stats = CreateDefaultSubobject<UTenFeStatsComponent>(TEXT("Stats"));
    Equipment = CreateDefaultSubobject<UTenFeEquipmentComponent>(TEXT("Equipment"));
}

void ATenFeCharacter::BeginPlay()
{
    Super::BeginPlay();

    Stats->OnDeath.AddDynamic(this, &ATenFeCharacter::HandleDeath);
    Equipment->OnEquipmentChanged.AddDynamic(this, &ATenFeCharacter::RefreshWeaponVisual);
    RefreshWeaponVisual();

    if (APlayerController* PlayerController = Cast<APlayerController>(GetController()))
    {
        HUDWidget = CreateWidget<UTenFeHUDWidget>(PlayerController, UTenFeHUDWidget::StaticClass());
        if (HUDWidget)
        {
            HUDWidget->SetCharacter(this);
            HUDWidget->AddToViewport(0);
        }

        EquipmentMenuWidget = CreateWidget<UTenFeEquipmentMenuWidget>(PlayerController, UTenFeEquipmentMenuWidget::StaticClass());
        if (EquipmentMenuWidget)
        {
            EquipmentMenuWidget->SetCharacter(this);
            EquipmentMenuWidget->AddToViewport(10);
            EquipmentMenuWidget->SetVisibility(ESlateVisibility::Collapsed);
        }
    }
}

void ATenFeCharacter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (bSprinting && !bEquipmentMenuOpen)
    {
        if (!Stats->ConsumeStamina(12.0f * DeltaTime))
        {
            StopSprint();
        }
    }
}

void ATenFeCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    PlayerInputComponent->BindAxis(TEXT("MoveForward"), this, &ATenFeCharacter::MoveForward);
    PlayerInputComponent->BindAxis(TEXT("MoveRight"), this, &ATenFeCharacter::MoveRight);
    PlayerInputComponent->BindAxis(TEXT("Turn"), this, &APawn::AddControllerYawInput);
    PlayerInputComponent->BindAxis(TEXT("LookUp"), this, &APawn::AddControllerPitchInput);

    PlayerInputComponent->BindAction(TEXT("Jump"), IE_Pressed, this, &ACharacter::Jump);
    PlayerInputComponent->BindAction(TEXT("Jump"), IE_Released, this, &ACharacter::StopJumping);
    PlayerInputComponent->BindAction(TEXT("Sprint"), IE_Pressed, this, &ATenFeCharacter::StartSprint);
    PlayerInputComponent->BindAction(TEXT("Sprint"), IE_Released, this, &ATenFeCharacter::StopSprint);
    PlayerInputComponent->BindAction(TEXT("Attack"), IE_Pressed, this, &ATenFeCharacter::PerformAttack);
    PlayerInputComponent->BindAction(TEXT("NextWeapon"), IE_Pressed, this, &ATenFeCharacter::CycleWeapon);
    PlayerInputComponent->BindAction(TEXT("ToggleEquipment"), IE_Pressed, this, &ATenFeCharacter::ToggleEquipmentMenu);
}

void ATenFeCharacter::MoveForward(float Value)
{
    if (!bEquipmentMenuOpen && Controller && !FMath::IsNearlyZero(Value))
    {
        const FRotator YawRotation(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
        AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X), Value);
    }
}

void ATenFeCharacter::MoveRight(float Value)
{
    if (!bEquipmentMenuOpen && Controller && !FMath::IsNearlyZero(Value))
    {
        const FRotator YawRotation(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
        AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y), Value);
    }
}

void ATenFeCharacter::StartSprint()
{
    if (!bEquipmentMenuOpen && Stats->CurrentStamina > 5.0f)
    {
        bSprinting = true;
        GetCharacterMovement()->MaxWalkSpeed = 680.0f;
    }
}

void ATenFeCharacter::StopSprint()
{
    bSprinting = false;
    GetCharacterMovement()->MaxWalkSpeed = BaseWalkSpeed;
}

void ATenFeCharacter::PerformAttack()
{
    if (bEquipmentMenuOpen || bAttackOnCooldown || Stats->IsDead() || !Stats->ConsumeStamina(18.0f))
    {
        return;
    }

    bAttackOnCooldown = true;
    const FTenFeItemDefinition Weapon = Equipment->GetEquippedWeapon();
    const float AttackRange = Weapon.Id == TEXT("hunter_spear") ? 230.0f : 155.0f;
    const FVector Center = GetActorLocation() + GetActorForwardVector() * AttackRange;

    TArray<FOverlapResult> Hits;
    FCollisionQueryParams QueryParams(SCENE_QUERY_STAT(TenFeAttack), false, this);
    GetWorld()->OverlapMultiByChannel(Hits, Center, FQuat::Identity, ECC_Pawn, FCollisionShape::MakeSphere(75.0f), QueryParams);

    for (const FOverlapResult& Hit : Hits)
    {
        if (AActor* Target = Hit.GetActor(); Target && Target != this)
        {
            FDamageEvent DamageEvent;
            Target->TakeDamage(Weapon.Damage, DamageEvent, GetController(), this);
        }
    }

    FTimerHandle CooldownHandle;
    GetWorldTimerManager().SetTimer(CooldownHandle, [this]() { bAttackOnCooldown = false; }, 0.55f, false);
}

void ATenFeCharacter::CycleWeapon()
{
    if (!bEquipmentMenuOpen)
    {
        Equipment->CycleWeapon();
    }
}

float ATenFeCharacter::TakeDamage(float DamageAmount, FDamageEvent const& DamageEvent, AController* EventInstigator, AActor* DamageCauser)
{
    Super::TakeDamage(DamageAmount, DamageEvent, EventInstigator, DamageCauser);
    return Stats->ApplyDamage(DamageAmount, Equipment->GetTotalDefense());
}

void ATenFeCharacter::ToggleEquipmentMenu()
{
    if (!EquipmentMenuWidget || Stats->IsDead())
    {
        return;
    }

    bEquipmentMenuOpen = !bEquipmentMenuOpen;
    EquipmentMenuWidget->SetVisibility(bEquipmentMenuOpen ? ESlateVisibility::Visible : ESlateVisibility::Collapsed);
    StopSprint();

    if (APlayerController* PlayerController = Cast<APlayerController>(GetController()))
    {
        PlayerController->bShowMouseCursor = bEquipmentMenuOpen;
        if (bEquipmentMenuOpen)
        {
            FInputModeGameAndUI InputMode;
            InputMode.SetWidgetToFocus(EquipmentMenuWidget->TakeWidget());
            InputMode.SetHideCursorDuringCapture(false);
            PlayerController->SetInputMode(InputMode);
        }
        else
        {
            PlayerController->SetInputMode(FInputModeGameOnly());
        }
    }
}

void ATenFeCharacter::HandleDeath()
{
    StopSprint();
    GetCharacterMovement()->DisableMovement();
    if (APlayerController* PlayerController = Cast<APlayerController>(GetController()))
    {
        DisableInput(PlayerController);
    }
}

void ATenFeCharacter::RefreshWeaponVisual()
{
    const int32 WeaponIndex = Equipment ? Equipment->EquippedWeaponIndex : 0;
    switch (WeaponIndex)
    {
        case 1:
            WeaponVisual->SetRelativeScale3D(FVector(0.12f, 0.12f, 1.25f));
            break;
        case 2:
            WeaponVisual->SetRelativeScale3D(FVector(0.07f, 0.07f, 1.6f));
            break;
        default:
            WeaponVisual->SetRelativeScale3D(FVector(0.08f, 0.08f, 0.85f));
            break;
    }
}
